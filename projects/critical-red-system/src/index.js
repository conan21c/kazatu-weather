/**
 * CriticalRedSystem — 메인 진입점
 * 
 * 사양서 v7.0 통합 모듈
 */

import { RiskCalculator } from './core/risk-calculator.js';
import { VisualEngine, PALETTE } from './core/visual-engine.js';

// 📦 공개 API — 외부에서 호출 가능한 인터페이스
class CriticalRedSystem {
  constructor(options = {}) {
    this.options = options;
    
    // 시스템 상태
    this.status = {
      initialized: false,
      level: 'safe',
      value: 0,
      lastUpdate: null
    };

    console.log(`🚀 CriticalRedSystem v7.0 — 옵션: ${JSON.stringify(options)}`);
  }

  /**
   * 시스템 초기화 — 설정 로드 및 컴포넌트 연결
   */
  initialize() {
    this.engine = new VisualEngine(this.options);
    
    if (!this.engine.connect()) {
      console.error('❌ CriticalRedSystem 초기화 실패 — targetSelector 찾을 수 없음');
      return false;
    }

    // 기본 데이터 로드 (옵션에서 또는 환경 변수)
    const initialData = this.loadInitialData();
    
    // 상태 업데이트 및 표시
    this.updateState(initialData);

    this.status.initialized = true;
    console.log('✅ CriticalRedSystem 초기화 완료 — 상태:', this.getStatus());
    
    return true;
  }

  /**
   * 외부에서 데이터 입력 받기
   */
  setInput(data) {
    if (!this.engine || !this.engine.dom) {
      console.warn('⚠️ 시스템 연결되지 않음. 먼저 initialize() 호출하세요.');
      return false;
    }

    const result = RiskCalculator.aggregateRisk([data]);
    
    this.updateState(result);
    
    // 시각적 업데이트
    const chartData = RiskCalculator.toChartData(result.value);
    this.engine.update(chartData);
    
    console.log(`📝 데이터 입력: ${JSON.stringify(data)}`);
    return result;
  }

  /**
   * 외부에서 위험도 직접 설정 — 테스트/디버깅용
   */
  setRisk(value, level = RiskCalculator.determineLevel(value)) {
    const chartData = RiskCalculator.toChartData(value);
    
    this.updateState({ ...chartData.current, value });
    this.engine.update(chartData);
    
    console.log(`🔧 위험도 직접 설정: value=${value}, level=${level}`);
    return true;
  }

  /**
   * 초기 데이터 로드 — 환경 변수 또는 기본값
   */
  loadInitialData() {
    // 환경 변수 우선 (보안)
    const envValue = Number(process.env.CRITICALRED_VALUE || 0);
    
    if (!isNaN(envValue)) {
      return { value: envValue };
    }

    // 기본 테스트 데이터 — 사양서 예시
    return { 
      value: 28,          // 임계점 근처 (경고 표시)
      baseline: 50,
      multiplier: 1.2
    };
  }

  /**
   * 현재 상태 반환 — 외부에서 읽기용 API
   */
  getStatus() {
    return {
      ...this.status,
      chartData: RiskCalculator.toChartData(this.status.value),
      thresholds: [
        { name: 'safe', threshold: 0 },
        { name: 'warning', threshold: 10 },
        { name: 'critical', threshold: 25 },
        { name: 'severe', threshold: 40 }
      ]
    };
  }

  /**
   * 상태 업데이트 — 내부 로직 변경 반영
   */
  updateState(data) {
    const result = RiskCalculator.aggregateRisk([data]);
    
    this.status = {
      ...this.status,
      value: result.value,
      level: result.level,
      lastUpdate: new Date().toISOString()
    };

    // 시각적 업데이트
    if (this.engine) {
      const chartData = RiskCalculator.toChartData(result.value);
      this.engine.update(chartData);
    }

    console.log(`📊 상태 업데이트: level=${result.level}, value=${result.value.toFixed(1)}%`);
    
    return result;
  }

  /**
   * 외부 이벤트 리스너 등록 — 반응형 패턴
   */
  on(event, callback) {
    if (typeof event !== 'string' || typeof callback !== 'function') return false;
    
    this.eventListeners = this.eventListeners || {};
    this.eventListeners[event] = [...(this.eventListeners[event] || []), callback];
    
    // 이벤트 발생 시 호출
    if (event === 'level-change') {
      setTimeout(() => callback(this.getStatus()), 100);
    }

    console.log(`📡 이벤트 리스너 등록: ${event}`);
    return true;
  }

  /**
   * 시스템 상태 변경 감지 — 자동 알림
   */
  detectLevelChange() {
    const prevLevel = this.status.level;
    
    if (!prevLevel || prevLevel === 'safe') return false;
    
    // 레벨이 safe → 다른 상태로 변화하면 알림
    console.log(`🔔 레벨 변경 감지: ${prevLevel} → ${this.status.level}`);
    return true;
  }

  /**
   * 시스템 점검 — 자가 진단
   */
  selfCheck() {
    const checks = [
      ['initialized', this.status.initialized, '시스템 초기화 여부'],
      ['engine.connected', !!this.engine.dom, '시각 엔진 연결 상태'],
      ['status.level', this.status.level !== null, '상태 값 설정 여부']
    ];

    console.log('🛠️ CriticalRedSystem 자가진단:');
    
    let passed = 0;
    checks.forEach(([key, value, desc]) => {
      const status = value ? '✅' : '❌';
      console.log(`  ${status} ${desc}: ${value}`);
      if (value) passed++;
    });

    return passed === checks.length;
  }

  /**
   * 시스템 종료 — 리소스 해제
   */
  destroy() {
    this.engine?.reset();
    this.status = {};
    
    console.log('🏁 CriticalRedSystem 종료 — 리소스 해제 완료');
    
    return true;
  }
}

// 🔧 모듈 내보내기
export default CriticalRedSystem;
export { RiskCalculator, VisualEngine, PALETTE };

// UMD 포맷 — 브라우저 호환성
if (typeof window !== 'undefined') {
  window.CriticalRedSystem = CriticalRedSystem;
  
  // 자동 초기화 — 환경 변수에서 설정 로드
  if (process.env.CRITICALRED_AUTO_INIT === 'true') {
    const system = new CriticalRedSystem({ 
      targetSelector: '.critical-red-container',
      background: PALETTE.deepSlateBlue
    });
    
    setTimeout(() => system.initialize(), 0);
  }
}

/**
 * 데모 HTML 생성 — 개발 환경용 빠른 테스트
 */
if (process.env.NODE_ENV === 'development' && typeof require !== 'undefined') {
  const demo = () => {
    console.log('🧪 CriticalRedSystem 데모 시작\n');
    
    // 가상 DOM 생성
    const mockHTML = `
      <!DOCTYPE html>
      <html lang="ko">
        <head>
          <meta charset="UTF-8">
          <title>CriticalRedSystem Demo</title>
          <style>
            body { 
              background: ${PALETTE.deepSlateBlue}; 
              padding: 2rem;
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            
            #critical-red-container {
              min-height: 150px;
              margin-top: 2rem;
            }

            .controls {
              display: flex;
              gap: 1rem;
              margin-bottom: 1rem;
            }
            
            button {
              padding: 0.5rem 1rem;
              background: ${PALETTE.mutedGold};
              border: none;
              border-radius: 4px;
              cursor: pointer;
            }
          </style>
        </head>
        <body>
          <h1>CriticalRedSystem v7.0 — 데모</h1>
          
          <div class="controls">
            <button onclick="system.setInput({ value: 5 })">-safe (5%)</button>
            <button onclick="system.setInput({ value: 12 })">-warning (12%)</button>
            <button onclick="system.setInput({ value: 30 })">-critical (30%)</button>
            <button onclick="system.setInput({ value: 45 })">-severe (45%)</button>
            <button onclick="system.setRisk(25)">-임계점 정확히</button>
          </div>

          <div id="critical-red-container"></div>
          
          <pre id="output"></pre>
        </body>
      </html>
    `;
    
    console.log(mockHTML);
    
    return mockHTML;
  };

  if (typeof module !== 'undefined') {
    module.exports = CriticalRedSystem;
  }
}