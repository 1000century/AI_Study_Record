## langchain을 이용한 RAG 구현
- 실습 날짜: 25.03.25 (화)
- [링크 깃허브 참고](https://github.com/teddynote-lab/mcp-usecase)

### `load_documents 함수` 변경
- pdf 파일들 경로-> HTML 파일들 경로
- (리스트로 들어가야 함)
```python
def load_documents(self, source_uris: List[str]) -> List[Document]:
    docs = []
    for source_uri in source_uris:
        if not os.path.exists(source_uri):
            print(f"File not found: {source_uri}")
            continue
        
    print(f"Loading PDF: {source_uri}")
    loader = PDFPlumberLoader(source_uri)
    docs.extend(loader.load())

    return docs```

def load_documents(self, source_uris: List[str]) -> List[Document]:
    docs = []
    for source_uri in source_uris:
        if not os.path.exists(source_uri):
            print(f"File not found: {source_uri}")
            continue
            
        print(f"Loading HTML: {source_uri}")
        loader = UnstructuredHTMLLoader(source_uri)
        docs.extend(loader.load())
    
    return docs
```

### 결과
| query | type | result |
|-------|------|--------|
| '심실빈맥의 치료' | semantic_search | ## Search Results<br>### Result 0<br>순환기###심실 빈맥 (Ventricular tachycardia, VT)<br>(1720, '심실빈맥 (VT)', 'basic', 1)<br>심전도: Wide QRS<br>Monomorphic VT: Regular, QRS 일정한 모양<br>... [나머지 내용] |
|'당뇨병의 진단 기준' | keyword_search | <br>## Search Results<br>### Result 0<br>임신성 당뇨병의 고위험군 기준:<br>① 임신 전 비만한 경우 (체질량 지수≥30kg/m2)<br>② 2형 당뇨병의 가족력<br>③ 이전에 임신성 당뇨병이 있었던 경우, 내당능장애 또는 요당의 과거력(glucosuria)<br>임신 후 첫 병원 방문 시 시행한 검사상 당뇨 진단 기준을 만족한다면 현성 당뇨병이 있었던 것으로 진단한다.<br>[1] 산과학 6판, pg.151-152, 912<br>Source: html_file_30. 산과_3. 산전 관리 1- 임신의 진단과 관리_3. 산전 관리 1- 첫 방문 (보통 5-7주 경)_544.html<br>---<br>### Result 1<br>내분비###당뇨병<br>(1287, '당뇨병 진단 및 분류', 'basic', 1)<br>(1) 당뇨병 진단<br>1) 당뇨병 진단 기준<br>다음,다뇨,체중감소 + 무작위 혈당 ≥ 200mg/dL<br>공복 혈당(FPG) ≥ 126mg/dL<br>75g 경구당부하검사(OGTT) 2시간 후 ≥ 200mg/dL<br>HbA1c ≥ 6.5%<br>1 경우: 그 자체로 재검 없이 확진 가능<br>2 ~ 4 경우: 두가지 진단 기준을 동시에 충족시 확진 가능<br>2 ~ 4 경우 중 둘 중 하나만 진단 기준에 맞으면 둘 중 높았던 값을 재검<br>2) 임신성 당뇨병 진단 기준<br>1단계 접근법 : 공복 75g 경구당부하검사 (OGTT)<br>공복≥ 92, 1hr≥ 180, 2hr≥ 153 (1가지 이상시 진단)<br>2단계 접근법<br>선별검사:<br>비공복 50g 경구당부하검사(OGTT)<br>(언제든) = 1시간후 ≥ 140 (확진검사 시행)<br>확진검사: 100g 경구당부하검사 (OGTT) 다음중 2가지 이상 양성<br>공복≥ 95, 1hr≥ 180, 2hr≥ 155, 3hr≥ 140 “9580-5540”<br>3) 당뇨병 전단계 기준<br>공복혈당장애 (IFG) : 100 ≤ FPG ≤ 125<br>Source: html_file_5. 내분비_6. 당뇨병_1. 당뇨병_281.html<br>---<br>### Result 2<br>산과###임신 전 당뇨병 (pregestational diabetes)<br>(3287, '임신 전 당뇨병 (Pregestational Diabetes)', 'basic', 1)<br>정의: 임신 전에 당뇨병을 진단받거나, 임신 중에 당뇨병의 진단기준을 만족하는 경우<br>** 당뇨병의 진단기준 (내분비 > 당뇨병 참고)<br>다음,다뇨,체중감소 + 무작위 혈당 ≥ 200mg/dL<br>공복 혈당(FPG) ≥ 126mg/dL<br>75g 경구당부하검사(OGTT) 2시간 후 ≥ 200mg/dL<br>HbA1c ≥ 6.5%<br>동의어: 임신 전 당뇨병 = pregestational diabetes = 현성 당뇨병 = overt diabetes<br>영향: 임신 전 당뇨병을 진단받은 임산부는, 임신성 당뇨병보다 태아와 산모에게 더 많은 영향을 끼지는 것으로 알려져 있다.<br>태아에게 미치는 영향<br>자연 유산, 조산, 설명되지 않는 사산<br>Source: html_file_30. 산과_24. 임신 중 당뇨병_2. 임신 전 당뇨병 (pregestational diabetes)_1401.html<br>---<br>### Result 3<br>류마티스###전신홍반루푸스 (SLE)<br>(1338, '전신홍반루푸스 (SLE)', 'basic', 1)<br>진단 기준<br>다음 17개의 분류 기준 중 적어도 1개 이상의 임상적 기준과, 1개 이상의 면역학적 기준을 포함하는 4개 이상의 기준을 만족하는 경우 (2012 SLICC classification criteria)<br><br>2019 EULAR/ACR SLE classification criteria<br><br>위와 같은 기준들을 활용하여, 임상증상과 실험실 검사 소견을 종합하여 진단<br>검사<br>자가 항체: Anti-nuclear Ab (ANA), Anti-dsDNA Ab, Anti-Sm Ab, Anti-phospholipid Ab<br>질병활성도 : Anti-dsDNA▲ / C3, C4, CH50▼<br>그 밖의 혈액, 소변, 영상 검사 등 필요한 검사 시행<br>치료<br>모든 환자에서 Hydoroxychloroquine과 같은 Antimalarial drug 사용<br>주요 장기 침범 X: NSAIDs, low dose steroid 등 대증 치료<br>주요 장기 침범 O (신장, CNS 등) : 고용량 Glucocorticoid ± 면역억제제<br>Source: html_file_6. 류마티스_1. 전신홍반루푸스 (SLE)_1. 전신홍반루푸스 (SLE)_368.html<br>---<br>### Result 4<br>부인과###쿠싱 증후군<br>(3243, '쿠싱증후군', 'basic', 1)<br><br>쿠싱증후군은 혈중 glucocorticoid의 만성적 상승에 의한 임상적 상태로, 쿠싱증후군이 있는 여성환자들은 고안드로겐 혈증이 동반되며 이로 인한 월경불순, 무월경, 다모증, 여드름 등의 증상이 발생할 수 있다.<br>자세한 진단 기준 및 치료는 내분비내과 > 쿠싱증후군 단원을 참고<br>[1] 부인과학, 6판. pg. 488-489<br>Source: html_file_40. 부인과_10. 이차성 무월경_8. 쿠싱 증후군_1416.html<br>---|