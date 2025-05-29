# HTML 문서 RAG 구현

로컬 HTML 파일을 불러와 OpenAI 임베딩을 통해 문서 벡터화하고, 유사도 기반 검색 기능을 구현하는 Flask기반 어플리케이션


## 주요 기능

📂 `HTML 문서 로딩`: html_files 폴더 내 모든 HTML 문서 로드
```python
for idx,file_name in enumerate(os.listdir(folder_path)):
    file_path = os.path.join(folder_path, file_name)

    loader = UnstructuredHTMLLoader(file_path)
    data = loader.load()

    chap = data[0].page_content.split('\n')[0].split('##')[0]
    remove_first_line = '\n'.join(data[0].page_content.split('\n')[1:])
    final_content = f"단원명: {chap}\n\n{remove_first_line}"

    docs.append({"filename": file_name, "content": final_content})
    documents.append(Document(page_content=final_content, metadata={"filename": file_name}))
```

🧠 `OpenAI 임베딩`: text-embedding-3-small 모델로 문서 임베딩 수행
```python
embedding = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=api_key)
vectorstore = Chroma(
    collection_name="medical",
    embedding_function=embedding,
    persist_directory="chroma_db"
)
for i in range(0, len(documents), 100):
    vectorstore.add_documents(documents[i:i + 100])
    logger.info(f"문서 {i + 1}~{min(i + 100, len(documents))} 저장 완료")
```

🔎 `유사도 기반 검색`: 입력된 키워드와 가장 유사한 문서 5개 반환
```python
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
results = retriever.invoke(query)
```

📜 `문서 상세 보기`: 문서 제목 및 내용 렌더링

🌐 `원본 HTML 보기`: 원문 HTML 파일 그대로 보기 기능 제공


## 사용 방법

1. html_files/ 폴더에 HTML 문서를 넣기.


2. 앱 실행 후 웹 페이지 접속 (localhost:5000)


3. OpenAI API 키를 입력하면 문서가 자동으로 임베딩 진행.


4. 문서 목록, 검색, 원본 보기 등 웹 UI 제공



## 🛠️ 기술 스택

Python / Flask

LangChain / OpenAI / Chroma

HTML 문서 파싱: UnstructuredHTMLLoader



---

## 결과
| query 1. 당뇨병 | : |  |
|:-----|:------|:-------|
|<br>            단원명: 감염<br><br>(1341, '묘소병(고양이할큄병, 바르토넬라 감염)', 'basic', 1)<br><br>Bartonella henselae (고양이) 등 : 그람음성 막대균<br>고양이 접촉력, 긁힌 병터(Primary inoculation lesion), 국소림프절병증 있을 경우 의심<br>증상 : 원발 병터에 무통성 홍반구진/농토, 국소림프절병증<br>진단 : 중합효소연쇄반응(PCR), 혈청검사<br>치료<br>심한 림프절병증 경우 : Azithromycin<br>화농림프절 : 바늘로 배농 (단, 절개 배농은 금지|단원명: 감염<br><br>(360, '광견병(공수병)', 'basic', 1)<br>랍도바이러스과의 하나, RNA 바이러스<br>전파: 교상 부위에 바이러스가 함유된 타액이 침투<br>초기증상: 발열, 근육통, 두통, 불안 및 초조, 물린 부위 이상감각 및 통증 또는 가려움<br>양상: 뇌염형, 마비형<br>뇌염형(80%) : 발열, 혼돈, 환가, 공격성, 근경련, 과민행동, 발작, 물공포증(공수증), 공기공포증<br>마비형(20%) : 근력약화, 활약근 침범 흔함<br>의심: 비전형적 급성 뇌염 또는 길랑-바레증후군을 포함한 급성 이완성 마비를 보일 경우<br>진단: RT-PCR, 직접형광항체검사(피부조직에서 모낭 아래 피부신경에서 광견병 바이러스 항원 발견)<br>치료: 확립된 치료 없음<br>광견병 노출 후 예방<br>사람을 문 동물을 잡아 10일간 관찰 : 건강하면 치료 필요 없음<br>광견병 면역글로불린(RIG)와 백신투여 : 동물이 도망가거나 죽은 경우, 동물이 미친 증상 보이는 경우<br>야생동물은 즉시 죽여 형광항체 검사 실시해 뇌조직에 바이러스 항원 유무 확인    |단원명: 비뇨의학<br><br>(2377, '요로생식기 결핵', 'basic', 1)<br>분류 및 증상<br>신장과 요관 결핵<br>무증상~renal colic<br>방광결핵<br>배뇨통, 빈뇨, 야간뇨, 혈뇨<br>생식기 결핵<br>무증상<br>진단<br>소변검사<br>배양검사가 음성인 농뇨<br>Tuberculin test<br>치료<br>항결핵제|
|단원명: 감염<br><br>(1329, '거대세포 바이러스', 'basic', 1)<br><br>거대세포바이러스(cytomegalovirus; CMV): 감염된 상피세포가 주변의 세포보다 2-4배 크고 핵내 봉입체(올빼미 눈 모양) 가짐,<br>양상: 선천성 CMV 감염, 주산기 CMV 감염, 면역저하자 CMV 감염<br>선천성 감염: 점출혈, 간비장비대, 황달, 소뇌증, 자궁내 성장지연 등<br>면역저하자 CMV: 발열, 권태감, 식욕부진, 야간발한, 관절통, 근육통, 간기능이상, 백혈구감소증, 혈소판감소증, 비전형 림프구 증가, 위장관출혈 및 궤양 등<br>진단: PCR, 감염된 세포에서 Owl’s eye관찰 (eosinophilic intranuclear inclusion)<br>치료: Ganciclovir, Valganciclovir|단원명: 감염<br><br>(399, '큐열', 'basic', 1)<br>원인균: Coxiella burnetii<br>인수공통감염병 (감염된 소, 양, 염소, 고양이, 개 , 토끼 등)<br>증상: 발열, 극심한 피로감, 눈부심, 주로 안구후면의 심한 두통 등<br>진단: 간접면역형광법 (TOC)<br>치료: Doxycycline, 임신시 trimethoprim-sulfamethoxazole (TMP-SMX)||

|query| 검색된 문서들|
|---|---|
|심부전으로 입원한 환자에게 처음 시행해야 할 처치는?|응급의학_2. 외상 환자의 응급처치_1. 응급처치<br>외과_9. 심폐소생술_2. 성인 전문소생술 (ACLS) - 심정지 1 - 심정지 인지 및 기본 소생술(BLS)<br>외과_5. 수술 전 처치_9. 수술 전후 심부정맥혈전 예방 (perioperative VTE prophylaxis)<br>부인과_19. 자궁 경부암_2. 자궁 경부암 (Cervical cancer)_1424 <br> _-4. 전공의 내과_1. 의료관련감염 예방_1. 손위생_1319 |
|수술 후 발생 가능한 DVT 예방 방법은?|<br>순환기_19. 말초혈관질환_7. 심부정맥혈전증 (DVT)<br>외과_5. 수술 전 처치_9. 수술 전후 심부정맥혈전 예방 (perioperative VTE prophylaxis)<br>순환기_19. 말초혈관질환_4. 급성 동맥 폐색<br>외과_5. 수술 전 처치_3. 수술 전 계통별 평가 1- 심혈관계 평가<br>신경과_2. 뇌혈관질환_4. 허헐성 뇌졸중_1229 |
|분만 중 자궁수축 억제제 사용 기준은?| _0. 순환기_21. 실신_3. 기립성 저혈압<br>외과_3. 수혈_4. 동결침전제제 (Cryoprecipitate) <br>산과_23. 임신 중 고혈압 질환_6. 전자간증 치료<br>신장_12. 그외 질환들_1. 부종<br>산과_14. 조산_3. 조기산통 (Preterm Labor, PTL)_1348 |
|조기진통 시 자궁 억제약 처방 기준?|<br>산과_14. 조산_3. 조기산통 (Preterm Labor, PTL)<br>산과_21. 조기 산후 출혈_2. 자궁이완증(자궁근육무력증, uterine atony)<br>산과_5. 분만 관리 1- 정상 분만_2. 정상 분만의 요소 2- Power - 자궁의 수축력 요소 (분만진통)<br>부인과_16. 자궁 체부 양성 질환_2. 자궁샘근육증<br>순환기_17. 고혈압_3. 고혈압 치료_106 |
|열성 경련 1차 대응은?|응급의학_1. 심폐소생술_4. 기도 이물에 대한 응급처치<br>정신과_4. 우울장애_2. 정상-병적 애도반응<br>정신과_17. 신경발달장애_6. 운동장애<br>정신과_10. 급식 및 섭식장애_3. 폭식장애<br>정신과_7. 외상 및 스트레스 관련 장애_5. 탈억제성 사회적 유대감 장애_906 |
|뇌전증 환자의 약 조절 기준은?|<br>외과_5. 수술 전 처치_7. 수술 전 계통별 평가 5- 내분비계 평가<br>외과_9. 심폐소생술_11. 신생아 소생술 (Neonatal resuscitation)<br>외과_12. 화상_1. 화상<br>순환기_12. 판막질환_2. 판막질환 요약<br>순환기_11. 심부전_2. 만성 심부전_82 |
|전자간증 기준 혈압 수치는?|<br>순환기_17. 고혈압_1. 혈압 측정<br>순환기_17. 고혈압_2. 고혈압 환자의 평가<br>순환기_21. 실신_3. 기립성 저혈압<br>산과_23. 임신 중 고혈압 질환_1. 임신 중 고혈압 질환 개요<br>산과_23. 임신 중 고혈압 질환_4. 임신성 고혈압, 만성 고혈압_571 |
|심부전으로 입원한 환자의 초기 평가 항목은?|<br>응급의학_2. 외상 환자의 응급처치_1. 응급처치<br>순환기_11. 심부전_1. 심부전 개요<br>외과_10. 외상_14. 전문 외상 처치술 (ATLS)<br>외과_5. 수술 전 처치_2. 수술 전 위험도 평가_473 <br> _-4. 전공의 내과_3. 노인 의학_1. 포괄적 노인 평가_1310 |
|고관절 골절 수술 전 체크리스트는?|<br>소아과 각론_33. 골격계 질환_4. 일과성 고관절 활막염 _854 <br> _-3. 전공의 외과_6. 중심정맥관_2. 중심정맥관 감염<br>외과_5. 수술 전 처치_9. 수술 전후 심부정맥혈전 예방 (perioperative VTE prophylaxis)<br>감염_15. 성인 예방접종_4. 특수 상황_367 <br> _-3. 전공의 외과_10. 임상해부학_2. 골반 수술 시 합병증_1340 |
|당뇨병성 케톤산증 치료 단계별 접근 방법은?|<br>소아과 각론_27. 내분비 질환_6. 당뇨병 케톤산증(DKA)<br>내분비_6. 당뇨병_2. 당뇨병 케톤산증(DKA), 고혈당 고삼투압상태 (HHS)<br>감염_8. 스피로헤타병_2. 렙토스피라증<br>비뇨의학_5. 전립선비대증_1. 전립선 비대증<br>비뇨의학_1. 비뇨기 감염_1. 전립성염_1216 |
|소아 고열 진단 순서는?|<br>소아과 총론_13. 선천 기형_7. 입술갈림증(구순열), 구개열<br>소아과 각론_28. 중추 신경계 질환_1. 열성 경련<br>외과_9. 심폐소생술_7. 소아 전문소생술 (PALS) - 심정지<br>소아과 총론_9. 신생아 가사 및 신생아 소생술_2. 신생아 소생술<br>외과_8. 외과적 합병증 _1. 수술 후 발열_488 |
                
## 특이사항
모바일 환경의 Termux에서 Ubuntu를 설치하여 구현하였습니다. 


