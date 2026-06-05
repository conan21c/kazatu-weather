/**
 * CriticalRedSystem — 위험도 임계점 계산기
 * 
 * 사양서 v7.0 기준:
 * - Warning: 10% 임계점
 * - Critical: 25% 임계점  
 * - Severe: 40% 임계점
 * 
 * @module core/risk-calculator
 */

// 🎨 색상 팔레트 — 사양서 준수
const PALETTE = {
  // 배경 및 기본 톤
  deepSlateBlue: '#1e293b',      // Main background
  mutedGold: '#d4af37',          // Accent/Highlight
  
  // 임계점 경고 색상
  criticalRed: '#DC2626',        // 오직 위험/임계점에 사용
  warningOrange: '#F59E0B',      // 경계선 표시
  neutralGray: '#9CA3AF'         // 텍스트 보조색
  
};

/**
 * 임계점 계산기 — 데이터 기반 위험도 분류
 */
class RiskCalculator {
  /**
   * 위험도 레벨 정의
   */
  static get THRESHOLDS() {
    return {
      WARNING: 10,   // 10% 이상 경고
      CRITICAL: 25,  // 25% 이상 임계점
      SEVERE: 40     // 40% 이상 심각
    };
  }

  /**
   * 위험도 레벨 결정
   * @param {number} value — 계산된 위험도 (0-100%)
   * @returns {string} 'safe' | 'warning' | 'critical' | 'severe'
   */
  static determineLevel(value) {
    if (!Number.isFinite(value)) return 'unknown';
    
    const value = Math.min(100, Math.max(0, value)); // 0-100% 범위 제한
    
    if (value >= this.THRESHOLDS.SEVERE) return 'severe';
    if (value >= this.THRESHOLDS.CRITICAL) return 'critical';
    if (value >= this.THRESHOLDS.WARNING) return 'warning';
    
    return 'safe';
  }

  /**
   * 임계점 색상 반환
   * @param {string} level — 위험도 레벨
   * @returns {string} HEX 색상 코드
   */
  static getColor(level) {
    const colorMap = {
      safe: PALETTE.mutedGold,
      warning: PALETTE.warningOrange,
      critical: PALETTE.criticalRed,
      severe: PALETTE.criticalRed, // 더 강조된 빨강
      unknown: '#6B7280'
    };
    
    return colorMap[level] || PALETTE.neutralGray;
  }

  /**
   * 위험도 계산 함수 — 데이터 입력값 처리
   * @param {Object} data — 입력 데이터
   * @returns {number} 0-100 범위 위험도 수치
   */
  static calculateRisk(data) {
    // 기본값 설정 — NaN 처리
    const inputs = {
      value: data.value ?? 0,          // 주요 지표 (예: AI 자동화 비중)
      baseline: data.baseline ?? 50,   // 기준치 (중간점)
      multiplier: data.multiplier ?? 1,// 가중치
      floor: 0,                        // 하한선
      ceiling: 100                     // 상한선
    };

    // 선형 변환
    let risk = inputs.value * inputs.multiplier;
    
    // 기준점 상대적 거리 계산
    const deviation = Math.abs(inputs.baseline - inputs.value);
    risk += (deviation / inputs.baseline) * 20; // 기준점에서 벗어날수록 위험 증가

    // 가중치 적용 후 정규화
    risk = Math.min(100, Math.max(0, 
      ((risk - inputs.floor) / (inputs.ceiling - inputs.floor)) * 100
    ));

    return Number(risk.toFixed(2));
  }

  /**
   * 복합 위험도 계산 — 다중 지표 통합
   * @param {Array<Object>} metrics — 여러 지표 데이터 배열
   * @returns {Object} 통합 결과
   */
  static aggregateRisk(metrics) {
    if (!Array.isArray(metrics) || metrics.length === 0) {
      return { value: 0, level: 'safe', color: PALETTE.mutedGold };
    }

    // 각 지표별 위험도 계산 및 평균
    const weightedSum = metrics.reduce((sum, metric) => {
      const risk = this.calculateRisk(metric);
      return sum + (risk * (metric.weight ?? 1));
    }, 0);

    const totalWeight = metrics.reduce((sum, m) => sum + (m.weight ?? 1), 0);
    
    // 가중 평균 위험도
    let aggregatedRisk = totalWeight > 0 
      ? weightedSum / totalWeight 
      : 0;

    return {
      value: Number(aggregatedRisk.toFixed(2)),
      level: this.determineLevel(aggregatedRisk),
      color: this.getColor(this.determineLevel(aggregatedRisk))
    };
  }

  /**
   * 임계점 임계값 초과 여부 확인
   * @param {number} value — 위험도 값
   * @returns {Object} 상태 정보
   */
  static checkThreshold(value) {
    const level = this.determineLevel(value);
    
    return {
      isSafe: level === 'safe',
      thresholdReached: ['warning', 'critical', 'severe'].includes(level),
      currentLevel: level,
      color: this.getColor(level)
    };
  }

  /**
   * 위험도 추이 계산 — 시간 기반 변화 감지
   * @param {Array<number>} history — 과거 데이터 배열 [oldVal, newVal]
   * @returns {Object} 변화 정보
   */
  static analyzeTrend(history = []) {
    if (history.length < 2) return { trend: 'unknown', change: 0 };

    const [prevValue, currentValue] = history.slice(-2);
    const change = Math.abs(currentValue - prevValue);
    
    // 변화율 계산
    const percentageChange = prevValue > 0 
      ? ((currentValue - prevValue) / prevValue * 100).toFixed(1)
      : 0;

    return {
      trend: change > 5 ? 'increasing' : change < -5 ? 'decreasing' : 'stable',
      change,
      percentageChange: Number(percentageChange),
      alertTriggered: Math.abs(change) >= 10 // 10% 이상 변화 시 경고
    };
  }

  /**
   * 임계점 시각화 데이터 생성 — 차트용 JSON
   * @param {number} value — 현재 위험도
   * @returns {Object} 차트 렌더링용 객체
   */
  static toChartData(value) {
    const level = this.determineLevel(value);
    
    return {
      current: {
        value,
        label: `${value.toFixed(1)}%`,
        color: this.getColor(level),
        icon: this.getIconForLevel(level)
      },
      thresholds: [
        { name: 'safe', line: 0, color: PALETTE.mutedGold },
        { name: 'warning', line: this.THRESHOLDS.WARNING, color: PALETTE.warningOrange },
        { name: 'critical', line: this.THRESHOLDS.CRITICAL, color: PALETTE.criticalRed },
        { name: 'severe', line: this.THRESHOLDS.SEVERE, color: '#B91C1C' }
      ],
      levelLabel: level.toUpperCase()
    };
  }

  /**
   * 위험도별 아이콘 반환
   */
  static getIconForLevel(level) {
    const iconMap = {
      safe: '🟢',
      warning: '🟡',
      critical: '🟠', 
      severe: '🔴'
    };
    
    return iconMap[level] || '⚪';
  }

  /**
   * 테스트 유틸리티 — 로직 검증용
   */
  static runTests() {
    console.log('🧪 RiskCalculator Test Suite\n');

    // 기본 계산 테스트
    const tests = [
      { input: { value: 0, baseline: 50 }, expectedLevel: 'safe', desc: '최소값' },
      { input: { value: 25, baseline: 50 }, expectedLevel: 'warning', desc: '경계선' },
      { input: { value: 30, baseline: 50 }, expectedLevel: 'critical', desc: '임계점 도달' },
      { input: { value: 40, baseline: 50 }, expectedLevel: 'severe', desc: '심각도 도달' },
      { input: { value: 100, baseline: 50 }, expectedLevel: 'severe', desc: '최대값' }
    ];

    let passed = 0;
    
    tests.forEach(({ input, expectedLevel, desc }) => {
      const result = this.determineLevel(this.calculateRisk(input));
      const status = result === expectedLevel ? '✅ PASS' : `❌ FAIL (got ${result})`;
      
      if (result === expectedLevel) passed++;
      console.log(`${status} — ${desc}: input=${input.value}, expected=${expectedLevel}, got=${result}`);
    });

    console.log(`\n📊 결과: ${passed}/${tests.length} 테스트 통과\n`);
    
    return passed === tests.length;
  }
}

// 🔧 모듈 내보내기 (ESM 및 CommonJS 지원)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = RiskCalculator;
  
  // 자가 검증 실행 — 개발 환경에서 자동 테스트
  if (process.env.NODE_ENV === 'development') {
    console.log('🚀 CriticalRedSystem 모듈 로드됨');
    const testPassed = RiskCalculator.runTests();
    process.exitCode = !testPassed ? 1 : 0;
  }
}

// UMD 포맷 — 브라우저 및 Node.js 양쪽 호환
if (typeof window !== 'undefined') {
  window.RiskCalculator = RiskCalculator;
} else if (typeof module !== 'undefined' && module.exports) {
  module.exports = RiskCalculator;
}