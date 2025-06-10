import 'package:flutter/material.dart';
import '../utils/rag_service.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});
  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> with TickerProviderStateMixin {
  final RAGService rag = RAGService();
  final TextEditingController _controller = TextEditingController();
  List<Map<String, dynamic>> chunks = [];
  String answer = '';
  bool loading = false;
  final Set<int> expandedIndexes = {}; // 확장 상태 추적용
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    rag.init();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _runRAG() async {
    final query = _controller.text.trim();
    if (query.isEmpty) return;

    setState(() {
      loading = true;
      answer = '';
      chunks = [];
      expandedIndexes.clear();
    });

    try {
      final resultChunks = await rag.searchRelevantChunks(query);
      setState(() {
        chunks = resultChunks;
        loading = false;
        _tabController.index = 0;
      });

      final contexts = chunks.map((e) => e['text'] as String).toList();
      final response = await rag.generateAnswer(query, contexts);
      setState(() {
        answer = response;
        _tabController.index = 1;
      });
    } catch (e) {
      setState(() {
        answer = '에러 발생: $e';
        loading = false;
      });
    }
  }

  Widget _buildChunkItem(int index, Map<String, dynamic> chunk) {
    final isExpanded = expandedIndexes.contains(index);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ListTile(
          title: Text(
            '\${index + 1}. ' + (chunk['text'] as String).split('\n').first,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          trailing: Icon(isExpanded ? Icons.expand_less : Icons.expand_more),
          onTap: () {
            setState(() {
              if (isExpanded) {
                expandedIndexes.remove(index);
              } else {
                expandedIndexes.add(index);
              }
            });
          },
        ),
        if (isExpanded)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: Text(chunk['text'], style: const TextStyle(fontSize: 14)),
          ),
        const Divider(),
      ],
    );
  }

  Widget _buildTabs() {
    return Expanded(
      child: TabBarView(
        controller: _tabController,
        children: [
          // 문서 검색 탭
          chunks.isNotEmpty
              ? ListView.builder(
                  itemCount: chunks.length,
                  itemBuilder: (context, index) {
                    return _buildChunkItem(index, chunks[index]);
                  },
                )
              : const Center(child: Text('검색된 문서가 없습니다.')),

          // Gemini 응답 탭
          answer.isNotEmpty
              ? SingleChildScrollView(
                  padding: const EdgeInsets.all(12),
                  child: Text(answer, style: const TextStyle(fontSize: 16)),
                )
              : const Center(child: Text('아직 답변이 없습니다.')),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("RAG 의학 도우미"),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: '📄 문서 검색'),
            Tab(text: '💡 생성 응답'),
          ],
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: _controller,
              decoration: const InputDecoration(labelText: "질문을 입력하세요"),
              onSubmitted: (_) => _runRAG(),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: loading ? null : _runRAG,
              child: const Text("질문하기"),
            ),
            const SizedBox(height: 20),
            if (loading) const CircularProgressIndicator(),
            if (!loading) _buildTabs(),
          ],
        ),
      ),
    );
  }
}
