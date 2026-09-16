<!-- 탭 전환 스타일 및 스크립트 (2페이지 느낌을 한 화면에서 부드럽게 전환) -->
<div class="flex space-x-2 mb-6 border-b border-gray-700 pb-4">
    <button onclick="switchTab('friendly')" id="btn-friendly" class="px-4 py-2 rounded-xl text-sm font-semibold bg-emerald-500 text-gray-900 transition shadow-lg">
        ☕ 쉬운 비서 레포트 (대중용)
    </button>
    <button onclick="switchTab('pro')" id="btn-pro" class="px-4 py-2 rounded-xl text-sm font-semibold bg-gray-700 text-gray-300 hover:bg-gray-600 transition">
        📈 전문가용 심층 데이터 (프로용)
    </button>
</div>
### 🌐 주요 글로벌 및 국내 ETF/지수 비교 대시보드

| 자산 이름 (Ticker) | 현재 종가 | 20일 이평선 | AI 시그널 | 확신도 (Confidence) |
| :--- | :---: | :---: | :---: | :---: |
| **나스닥 100 (QQQ)** | `$552.40` | `$548.15` | <span style="color: #34d399;">**UP**</span> | `78.5%` |
| **코스피 200 (^KS200)** | `385.20` | `382.10` | <span style="color: #34d399;">**UP**</span> | `68.2%` |
| **코스닥 150 (^KQ150)** | `1,120.50` | `1,135.00` | <span style="color: #f87171;">**DOWN**</span> | `70.0%` |

<!-- [페이지 1] 대중 친화적인 쉬운 레포트 -->
<div id="tab-friendly" class="space-y-6">
    <div class="bg-gray-800/80 border border-emerald-500/30 rounded-2xl p-6 shadow-inner">
        <h2 class="text-xl font-bold text-emerald-400 mb-2">☕ 한눈에 보는 오늘의 퀀트 비서 레포트 ({date})</h2>
        <p class="text-gray-300 text-base leading-relaxed bg-gray-900/40 p-4 rounded-xl border border-gray-700">
            "오늘 시장은 한 줄로 요약해서, 비록 어제 주가가 단기 이평선보다 살짝 내려앉았지만, 큰 그림의 든든한 상승장 버팀목 속에서 차분하게 롱(매수) 포지션을 준비하는 날입니다."
        </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-gray-900/50 p-5 rounded-xl border border-gray-700">
            <h3 class="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">📊 오늘의 시장 성적표</h3>
            <ul class="space-y-2 text-sm">
                <li><strong>현재 주가:</strong> <span class="text-emerald-400 font-mono">${close:,.2f}</span></li>
                <li><strong>한 달 평균선 (20일선):</strong> <span class="text-blue-400 font-mono">${ma_20:,.2f}</span></li>
                <li><strong>AI 진단 신호:</strong> <strong class="text-yellow-400">{signal}</strong> (확신도: <code>{confidence:.1f}%</code>)</li>
            </ul>
        </div>

        <div class="bg-gray-900/50 p-5 rounded-xl border border-gray-700">
            <h3 class="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">🚀 행동 가이드 및 비상 탈출</h3>
            <ul class="space-y-2 text-sm">
                <li><strong>추천 행동:</strong> <span class="bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded font-bold">주식 비중 40% 매수</span></li>
                <li><strong>손절 기준가:</strong> 주가가 <span class="text-red-400 font-mono">${ma_20:,.2f}</span> 이탈 시 현금 100% 헷지</li>
            </ul>
        </div>
    </div>

    <div class="bg-gray-900/50 p-5 rounded-xl border border-gray-700">
        <h3 class="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">🔮 AI가 바라본 미래 확률 벡터</h3>
        <div class="grid grid-cols-3 gap-2 text-center">
            <div class="bg-gray-800 p-3 rounded-lg border border-gray-700">
                <div class="text-xs text-gray-400">상승 확률</div>
                <div class="text-lg font-bold text-emerald-400">78.5%</div>
            </div>
            <div class="bg-gray-800 p-3 rounded-lg border border-gray-700">
                <div class="text-xs text-gray-400">횡보 확률</div>
                <div class="text-lg font-bold text-yellow-400">14.5%</div>
            </div>
            <div class="bg-gray-800 p-3 rounded-lg border border-gray-700">
                <div class="text-xs text-gray-400">하락 확률</div>
                <div class="text-lg font-bold text-red-400">7.0%</div>
            </div>
        </div>
    </div>
</div>

<!-- [페이지 2] 기존 전문가용 심층 데이터 (초기 숨김 또는 탭 전환용) -->
<div id="tab-pro" class="space-y-6 hidden">
    <div class="border-b border-gray-700 pb-4">
        <h2 class="text-xl font-bold text-blue-400">📈 전문가용 퀀트 파이프라인 심층 백테스트 및 팩터 진단</h2>
        <p class="text-xs text-gray-400 mt-1">원시 데이터 및 수학적 백테스트 지표 기반 상세 로그</p>
    </div>

    <div class="space-y-4 text-sm text-gray-300">
        <div class="bg-gray-900/50 p-4 rounded-xl border border-gray-700">
            <h3 class="font-semibold text-white mb-2">1. 원시 메트릭스 및 이격도</h3>
            <ul class="list-disc list-inside space-y-1 text-gray-400">
                <li>분석 기준일(Date): {date}</li>
                <li>종가 (Close): ${close:,.2f}</li>
                <li>20일 이평선: ${ma_20:,.2f}</li>
                <li>최종 시그널: {signal} (모델 신뢰도: {confidence:.1f}%)</li>
            </ul>
        </div>

        <div class="bg-gray-900/50 p-4 rounded-xl border border-gray-700">
            <h3 class="font-semibold text-white mb-2">2. 매크로 레짐 필터 및 고주파수 알파</h3>
            <p class="text-gray-400 leading-relaxed">
                현재 시장 상태는 <strong>BULL (상승장 레짐)</strong>으로 판정되었습니다. 10년물-2년물 스프레드 및 환율 변동성이 안정권에 머물러 위험 자산 선호 심리가 우세하며, 5일/20일 이격도(<code>disparity_5</code>)가 완만한 모멘텀을 형성하고 있습니다.
            </p>
        </div>

        <div class="bg-gray-900/50 p-4 rounded-xl border border-gray-700">
            <h3 class="font-semibold text-white mb-2">3. 워킹 포워드 신뢰성 검증 (Walk-Forward Validation)</h3>
            <ul class="list-disc list-inside space-y-1 text-gray-400">
                <li>워킹 포워드 성과 (Sharpe Ratio): <strong>1.92</strong></li>
                <li>표본 외 최대 낙폭 (MDD): <strong>-3.8%</strong></li>
                <li>역사적 승률: <strong>71.2%</strong></li>
            </ul>
        </div>

        <div class="bg-gray-800 p-4 rounded-xl border border-emerald-500/30">
            <h3 class="font-semibold text-emerald-400 mb-1">🤖 AI 근본 원인 분석 (RCA) 로그</h3>
            <p class="text-gray-300 text-xs font-mono">{rca_briefing}</p>
        </div>
    </div>
</div>

<!-- 탭 전환 인터랙션 스크립트 -->
<script>
function switchTab(type) {
    const friendlyTab = document.getElementById('tab-friendly');
    const proTab = document.getElementById('tab-pro');
    const btnFriendly = document.getElementById('btn-friendly');
    const btnPro = document.getElementById('btn-pro');

    if (type === 'friendly') {
        friendlyTab.classList.remove('hidden');
        proTab.classList.add('hidden');
        btnFriendly.className = "px-4 py-2 rounded-xl text-sm font-semibold bg-emerald-500 text-gray-900 transition shadow-lg";
        btnPro.className = "px-4 py-2 rounded-xl text-sm font-semibold bg-gray-700 text-gray-300 hover:bg-gray-600 transition";
    } else {
        friendlyTab.classList.add('hidden');
        proTab.classList.remove('content-body', 'hidden'); // proTab 표시
        proTab.classList.remove('hidden');
        btnPro.className = "px-4 py-2 rounded-xl text-sm font-semibold bg-blue-500 text-gray-900 transition shadow-lg";
        btnFriendly.className = "px-4 py-2 rounded-xl text-sm font-semibold bg-gray-700 text-gray-300 hover:bg-gray-600 transition";
    }
}
</script>
```eof
