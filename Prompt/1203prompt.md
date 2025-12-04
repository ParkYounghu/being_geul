##### [gemini 노드, summary Prompt]

```

{{ $json.text }}

아래 내용을 바탕으로 청년층의 관심을 끌 수 있는 '제목'과 '요약'을 작성해줘.
반드시 아래 JSON 형식을 지켜서 출력해야 해. 설명이나 다른 말은 절대 하지 마.

[내용]
{{ $json.text }}

[제약 조건]
1. 제목 (title):
 - 청년들이 클릭하고 싶게 자극적이고 트렌디하게 (어그로성)
 - 쉼표(,) 절대 사용 금지
 - 공백 포함 20자 이내 (두 줄 분량)
2. 요약 (summary):
 - 핵심 내용만 간결하게
 - 쉼표(,) 절대 사용 금지
 - 공백 포함 50자 이내 (세 줄 분량)

[출력 포맷]
{
  "title": "여기에 제목 작성",
  "summary": "여기에 요약 내용 작성"
}

```

#### [Gemini 노드, Genre Prompt]

너는 대한민국 정책 데이터를 분류하는 AI야. 아래 [내용]을 읽고, [목록] 중에서 가장 적절한 카테고리를 딱 하나만 골라서 단어로만 답해줘. 부가 설명이나 문장 부호는 절대 넣지 마.

[목록]
- 금융/자산
- 취업/창업
- 주거/생활
- 교육/역량
- 복지/건강
- 참여/권리

[내용]
{{ $('Merge').item.json.text || '내용 없음' }}

#### [n8n Code 노드 Prompt]

```

n8n의 Code 노드(JavaScript)에서 사용할 코드를 작성해줘.

1. 입력 데이터 구조:
   - 데이터는 `items[0].json.result.youthPolicyList` 경로에 있는 배열이다.

2. 출력 데이터 구조:
   - 각 정책 항목을 순회하며 아래 4가지 필드를 가진 JSON 객체 배열을 반환해야 한다.
   - 필드: title, text, period, link

3. 필드별 매핑 및 로직 규칙:

   [title]
   - `plcyNm` 값을 사용하고, 없으면 "제목 없음"

   [text]
   - `plcySprtCn` 값을 사용

   [period] (아래 우선순위대로 1개만 적용)
   1순위: `reqstBeginEndDe` (문자열 그대로)
   2순위: `aplyBgngYmd`와 `aplyEndYmd`가 둘 다 있으면 "YYYY-MM-DD ~ YYYY-MM-DD" 형식으로 변환
   3순위: `bizPrdBgngYmd`와 `bizPrdEndYmd`가 둘 다 있으면 "(운영기간) YYYY-MM-DD ~ YYYY-MM-DD" 형식으로 변환
   4순위: 위 값이 모두 없으면 "상세 내용 참조"
   (* 날짜는 YYYYMMDD 형식이므로 대시(-)를 넣어 포맷팅할 것)

   [link] (아래 우선순위대로 체크하여 가장 먼저 값이 있는 것을 사용)
   1순위: `refUrlAddr2`
   2순위: `refUrlAddr1`
   3순위: `aplyUrlAddr`
   4순위: `etctUrl`
   5순위: `bizId` 값이 있으면 다음 URL 생성 -> `https://www.youthcenter.go.kr/youngPlcyUnif/youngPlcyUnifDtl.do?bizId={bizId}`
   6순위: 위 값이 모두 없으면 네이버 검색 URL 생성 -> `https://search.naver.com/search.naver?query={title}`

위 로직을 적용해서 깔끔한 JavaScript 코드를 작성해줘.

```

#### [Code 노드, 기업마당 http 노드 연결]

```

// CASE 2: 데이터 위치 설정
const rawDataList = items[0].json.jsonArray;

if (!rawDataList || !Array.isArray(rawDataList)) return [];

// 1. 필터링 (기존 로직 유지)
const keywords = ['창업']; 
const filteredResults = rawDataList.filter(item => {
  const allText = JSON.stringify(item);
  return keywords.every(key => allText.includes(key));
});

// 2. 데이터 매핑 (원하는 컬럼명으로 변환) - 여기가 핵심!
// API 응답 키값(supportBizNm 등)을 우리 DB 컬럼명(title 등)으로 매칭합니다.
const mappedResults = filteredResults.map(item => {
    return {
        json: {
            title: item.pblancNm,       // 공고 제목
            text: item.bsnsSumryCn,
            period: item.reqstBeginEndDe,   // 신청 기간 (키값 확인 필요)
            // 링크는 보통 pblancId 등을 조합하거나 url 필드가 따로 있음. 
            // API 응답에 'pblancUrl' 같은게 없다면 아래처럼 ID로 조합해야 할 수도 있습니다.
// link 부분만 이렇게 바꿔보세요
link: item.pblancUrl 
    ? (item.pblancUrl.startsWith('http') ? item.pblancUrl : `https://www.bizinfo.go.kr${item.pblancUrl}`)
    : `https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/A/${item.pblancId}/view.do`
        }
    }
});

return mappedResults;

```

### [Code 노드, 온통청년 http 연결]

```

// 1. 데이터 리스트 꺼내기
// (n8n 버전에 따라 items[0].json 혹은 $input.item.json 등이 될 수 있으나, 기존 코드 유지)
const rootData = items[0].json;
const policyList = (rootData.result && rootData.result.youthPolicyList) ? rootData.result.youthPolicyList : [];

const results = [];

for (const policy of policyList) {
  
  // 제목, 내용
  const title = policy.plcyNm || "제목 없음";        
  const text = policy.plcySprtCn || "";     

  // -------------------------------------------------------
  // [보완 1] 기간 채우기 전략 (3단계 방어)
  // -------------------------------------------------------
  let periodStr = "";

  // 1순위: 신청 기간 문자열 (reqstBeginEndDe)
  if (policy.reqstBeginEndDe) {
    periodStr = policy.reqstBeginEndDe;
  } 
  // 2순위: 신청 기간 날짜 (aplyBgngYmd)
  else if (policy.aplyBgngYmd && policy.aplyEndYmd) {
    const start = policy.aplyBgngYmd.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3');
    const end = policy.aplyEndYmd.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3');
    periodStr = `${start} ~ ${end}`;
  } 
  // 3순위: 다 없으면 '사업 운영 기간'이라도 보여주기
  else if (policy.bizPrdBgngYmd && policy.bizPrdEndYmd) {
    const start = policy.bizPrdBgngYmd.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3');
    const end = policy.bizPrdEndYmd.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3');
    periodStr = `(운영기간) ${start} ~ ${end}`;
  }
  // 4순위: 진짜 아무것도 없음
  else {
    periodStr = "상세 내용 참조";
  }

  // -------------------------------------------------------
  // [보완 2] 링크 채우기 전략 (요청하신 순서 적용)
  // -------------------------------------------------------
  let finalLink = "";
  
  // [요청 1순위] refUrlAddr2 (참조 URL 2)
  if (policy.refUrlAddr2) {
    finalLink = policy.refUrlAddr2;
  }
  // [요청 2순위] refUrlAddr1 (참조 URL 1)
  else if (policy.refUrlAddr1) {
    finalLink = policy.refUrlAddr1;
  }
  // 3순위: 직접 신청 주소 (aplyUrlAddr)
  else if (policy.aplyUrlAddr) {
    finalLink = policy.aplyUrlAddr;
  }
  // 4순위: 기타 URL (etctUrl)
  else if (policy.etctUrl) {
    finalLink = policy.etctUrl;
  }
  // 5순위: 다 없으면 '온통청년' 상세 페이지 (bizId 이용)
  // 반복문 안이므로 item.json.bizId가 아니라 policy.bizId를 써야 정확합니다.
  else {
     // bizId가 있으면 ID 기반 링크 생성
     if (policy.bizId) {
        finalLink = `https://www.youthcenter.go.kr/youngPlcyUnif/youngPlcyUnifDtl.do?bizId=${policy.bizId}`;
     } 
     // bizId조차 없으면 네이버 검색 (최후의 수단)
     else {
        finalLink = `https://search.naver.com/search.naver?query=${encodeURIComponent(title)}`;
     }
  }

  results.push({
    json: {
      title: title,
      text: text,
      period: periodStr,
      link: finalLink
    }
  });
}

return results;

```

#### [Code 노드, Merge 이후에 gemini로 요약 후 DB로 깔끔하게 보내기 위한 내용 정리(title, summary, period, link)]

```

return $input.all().map((item, index) => {
  try {
    // 1. [수정] summary 노드도 197개가 있으니, 내 순번(index)에 맞는 걸 가져옵니다.
    const summaryNodeItems = $('summary').all();
    
    // 짝이 안 맞을 경우 에러 처리
    if (!summaryNodeItems[index]) {
      throw new Error(`Summary 결과가 모자랍니다. (현재 순번: ${index})`);
    }

    const targetItem = summaryNodeItems[index];

    // 2. 텍스트 추출 (스크린샷에 보이는 경로: content.parts[0].text)
    // 안전하게 가져오기 위해 경로가 없으면 빈 문자열 처리
    let rawText = "";
    if (targetItem.json.content && targetItem.json.content.parts && targetItem.json.content.parts[0]) {
      rawText = targetItem.json.content.parts[0].text;
    } else {
      // 혹시 경로가 다를 경우를 대비해 최상위 text도 확인
      rawText = targetItem.json.text || "";
    }

    // 3. Markdown 코드 블록(```json ... ```) 제거 및 파싱
    // 문자열에서 첫 번째 '{'와 마지막 '}' 사이만 발라냅니다.
    const firstBrace = rawText.indexOf('{');
    const lastBrace = rawText.lastIndexOf('}');

    if (firstBrace !== -1 && lastBrace !== -1) {
      const jsonOnly = rawText.substring(firstBrace, lastBrace + 1);
      const parsedData = JSON.parse(jsonOnly);

      // 4. 결과 저장
      item.json.title = parsedData.title || parsedData.Title || "제목 없음";
      item.json.summary = parsedData.summary || parsedData.Summary || parsedData.description || "요약 없음";
    } else {
      throw new Error("JSON 형식({ ... })을 찾을 수 없습니다.");
    }

  } catch (error) {
    // 에러가 나면 원인을 출력하고, 원본 텍스트도 같이 보여줌 (디버깅용)
    item.json.error = error.message;
    // item.json.debug_raw = rawText; // 필요시 주석 해제
  }

  return item;
});

```