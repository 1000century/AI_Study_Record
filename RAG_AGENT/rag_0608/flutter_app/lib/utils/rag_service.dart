import 'dart:convert';
import 'dart:math';
import 'dart:io';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

final String _openAiApiKey = dotenv.env['OPENAI_API_KEY'] ?? '';
final String _geminiApiKey = dotenv.env['GEMINI_API_KEY'] ?? '';

class RAGService {
  late Database _db;

  Future<void> init() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'documents.db');

    if (!await File(path).exists()) {
      final data = await rootBundle.load('assets/documents.db');
      final bytes = data.buffer.asUint8List();
      await File(path).writeAsBytes(bytes, flush: true);
    }

    _db = await openDatabase(path);
  }

  Future<List<Map<String, dynamic>>> searchRelevantChunks(String query) async {
    final queryEmbedding = await _getEmbedding(query);
    List<Map<String, dynamic>> scored = [];

    // 전체 문서 개수 조회
    final countResult = await _db.rawQuery('SELECT COUNT(*) as count FROM documents');
    final totalCount = Sqflite.firstIntValue(countResult) ?? 0;

    const int batchSize = 1000;
    int offset = 0;

    // 배치 반복
    while (offset < totalCount) {
      final batch = await _db.query(
        'documents',
        columns: ['text', 'embedding'],
        limit: batchSize,
        offset: offset,
      );

      for (final row in batch) {
        final text = row['text'] as String;
        final rawEmbedding = row['embedding'];

        try {
          final embedding = List<double>.from(json.decode(rawEmbedding as String));
          final score = _cosineSimilarity(queryEmbedding, embedding);
          scored.add({'text': text, 'score': score});
        } catch (e) {
          print("Failed to parse embedding: $e");
        }
      }

      offset += batchSize;
    }

    // 유사도 기준 정렬 후 상위 10개 반환
    scored.sort((a, b) => b['score'].compareTo(a['score']));
    return scored.take(10).toList();
  }


  double _cosineSimilarity(List<double> a, List<double> b) {
    double dot = 0.0, normA = 0.0, normB = 0.0;
    for (int i = 0; i < a.length; i++) {
      dot += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    return dot / (sqrt(normA) * sqrt(normB));
  }

  Future<List<double>> _getEmbedding(String text) async {
    final response = await http.post(
      Uri.parse('https://api.openai.com/v1/embeddings'),
      headers: {
        'Authorization': 'Bearer $_openAiApiKey',
        'Content-Type': 'application/json'
      },
      body: json.encode({
        'input': text,
        'model': 'text-embedding-3-small'
      }),
    );

    final data = json.decode(response.body);
    return List<double>.from(data['data'][0]['embedding']);
  }

  Future<String> generateAnswer(String question, List<String> contexts) async {
    final prompt = '''당신은 의학 전문가입니다. 아래 문맥을 참고하여 질문에 포괄적으로 답하십시오.

문맥:
${contexts.join("\n")}

질문: $question

답변:''';

    final response = await http.post(
      Uri.parse('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$_geminiApiKey'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'contents': [
          {
            'parts': [
              {'text': prompt}
            ]
          }
        ]
      }),
    );

    final result = json.decode(response.body);

    final candidates = result['candidates'];
    if (candidates == null || candidates.isEmpty) {
      throw Exception('No candidates returned from Gemini API. Response: $result');
    }

    final content = candidates[0]['content'];
    if (content == null || content['parts'] == null || content['parts'].isEmpty) {
      throw Exception('No content parts returned from Gemini API. Response: $result');
    }

    return content['parts'][0]['text'];
  }
}
