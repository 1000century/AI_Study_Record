🧠 HTML 문서 검색 웹 앱

이 Flask 웹 애플리케이션은 로컬 HTML 파일을 불러와 OpenAI 임베딩을 통해 문서 벡터화하고, 유사도 기반 검색 기능을 제공합니다.

🚀 주요 기능

📂 HTML 문서 자동 로딩: html_files 폴더 내 모든 HTML 문서 자동 로드

🧠 OpenAI 임베딩: text-embedding-3-small 모델로 문서 임베딩 수행

🔎 유사도 기반 검색: 입력된 키워드와 가장 유사한 문서 5개 반환

📜 문서 상세 보기: 문서 제목 및 내용 렌더링

🌐 원본 HTML 보기: 원문 HTML 파일 그대로 보기 기능 제공


⚙️ 사용 방법

1. html_files/ 폴더에 HTML 문서를 넣습니다.


2. 앱 실행 후 웹 페이지 접속 (localhost:5000)


3. OpenAI API 키를 입력하면 문서가 자동 임베딩됩니다.


4. 문서 목록, 검색, 원본 보기 등 웹 UI 제공



🛠️ 기술 스택

Python / Flask

LangChain / OpenAI / Chroma

HTML 문서 파싱: UnstructuredHTMLLoader



---
