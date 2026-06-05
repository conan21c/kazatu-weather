/**
 * CriticalRedSystem — 시각적 변경 엔진
 * 
 * 사양서 v7.0 준수:
 * - Mobile-First 반응형 CSS 적용
 * - 임계점 도달 시 자동 색상 전환
 * - Deep Slate Blue 배경 + Muted Gold 강조
 * 
 * @module core/visual-engine
 */

import { RiskCalculator, PALETTE } from './risk-calculator.js';

/**
 * 시각적 변경 엔진 — DOM 및 스타일 관리
 */
class VisualEngine {
  constructor(options = {}) {
    this.config = {
      // 기본값
      targetSelector: options.targetSelector || '.critical-red-container',
      background: PALETTE.deepSlateBlue,
      accent: PALETTE.mutedGold,
      
      // 임계점 스타일 오버라이드
      warningStyle: { backgroundColor: '#FFF7ED', color: '#9A3412' },
      criticalStyle: { backgroundColor: '#FEF2F2', color: '#991B1B' },
      severeStyle: { backgroundColor: '#FFEBEE', color: '#991B1B' }
    };

    this.dom = null; // 초기화 전 null
    this.subscribers = []; // 반응형 구독자 패턴
    
    console.log('🎨 VisualEngine 초기화 — config:', options);
  }

  /**
   * DOM 요소 연결 및 이벤트 리스너 등록
   */
  connect() {
    const element = typeof this.config.targetSelector === 'string'
      ? document.querySelector(this.config.targetSelector)
      : this.config.targetSelector;
    
    if (!element) {
      console.warn('⚠️ targetSelector로 DOM 요소 찾을 수 없음:', this.config.targetSelector);
      return false;
    }

    this.dom = element;
    
    // 초기 스타일 적용
    this.applyStyle(this.getDefaultStyle());
    
    // 외부 데이터 변경 시 리액티브 업데이트
    window.addEventListener('message', (event) => {
      if (event.data && event.data.type === 'criticalred-update') {
        this.update(event.data.payload);
      }
    }, true);

    console.log('✅ VisualEngine 연결 완료 — selector:', this.config.targetSelector);
    return true;
  }

  /**
   * 기본 스타일 반환 — 사양서 준수
   */
  getDefaultStyle() {
    return {
      container: `
        background-color: ${this.config.background};
        border-left: 4px solid ${PALETTE.criticalRed};
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        transition: all 0.3s ease-in-out;
      `
    };
  }

  /**
   * 임계점 도달 시 스타일 변경
   */
  applyStyle(styleConfig) {
    if (!this.dom) return null;

    const styles = Object.entries(styleConfig).map(([key, value]) => 
      `${key}: ${value}`
    ).join('; ');

    this.dom.style.cssText = styleConfig.container + '\n' + styles;
    
    console.log(`🎨 스타일 적용: ${JSON.stringify(styleConfig)}`);
    return this.dom;
  }

  /**
   * 위험도 데이터로 시각적 업데이트
   * @param {Object} data — RiskCalculator.toChartData() 결과
   */
  update(data = {}) {
    if (!this.dom) {
      console.warn('⚠️ VisualEngine 연결되지 않음. 먼저 connect() 호출하세요.');
      return null;
    }

    const { current, thresholds, levelLabel } = data;
    
    // 상태별 스타일 결정
    let statusStyle = this.getDefaultStyle();
    
    if (current.level === 'warning') {
      Object.assign(statusStyle, this.config.warningStyle);
    } else if (current.level === 'critical') {
      Object.assign(statusStyle, this.config.criticalStyle);
    } else if (current.level === 'severe') {
      Object.assign(statusStyle, this.config.severeStyle);
    }

    // 임계점 도달 시 경고 표시 추가
    if (!statusStyle['--alert']) {
      statusStyle.setProperty('--alert', current.level !== 'safe');
    }

    // 아이콘 및 레이블 업데이트
    const content = `
      <div style="display: flex; align-items: center; gap: 0.5rem;">
        <span style="font-size: 1.5rem;">${current.icon}</span>
        <div style="flex: 1;">
          <strong>${levelLabel}</strong>
          <span style="display: block; color: ${current.color}; font-weight: bold;">
            ${current.label} — 임계점 도달
          </span>
        </div>
      </div>
    `;

    this.dom.innerHTML = content + this.dom.outerHTML.replace(/<div[^>]*>/, '');

    // 스타일 적용 후 DOM 다시 렌더링
    const newElement = document.createElement('div');
    newElement.style.cssText = statusStyle.container + '\n' + Object.entries(statusStyle).reduce((s, [k,v]) => s ? `${s};${k}:${v}` : v, '');
    
    // 기존 content 보존
    this.dom.innerHTML = '';
    this.dom.appendChild(newElement);

    console.log(`🔄 시각적 업데이트: level=${current.level}, color=${current.color}`);
  }

  /**
   * 외부 데이터 구독 — 반응형 패턴
   */
  subscribe(callback) {
    if (typeof callback !== 'function') return false;
    
    this.subscribers.push({ callback, id: Date.now() });
    console.log(`📡 구독자 추가: ${this.subscribers.length}개`);
    
    return true;
  }

  /**
   * 외부 데이터 푸시 — 내부 상태 변경 시 구독자에게 알림
   */
  notify(data) {
    this.subscribers.forEach(({ callback }) => {
      try {
        callback(data);
      } catch (error) {
        console.error('🚨 구독자 에러:', error, 'data:', data);
      }
    });
  }

  /**
   * 상태 리셋 — 초기화
   */
  reset() {
    if (this.dom) {
      this.applyStyle(this.getDefaultStyle());
      this.dom.innerHTML = '';
      
      console.log('🔄 VisualEngine 리셋 완료');
    }
    
    return this;
  }

  /**
   * 사양서 준수 여부自检
   */
  selfCheck() {
    const checks = [
      ['background-color', this.dom?.style.backgroundColor || '', PALETTE.deepSlateBlue],
      ['border-left', this.dom?.style.borderLeft || '', '4px solid #DC2626'],
      ['padding', this.dom?.style.padding || '', '1rem']
    ];

    const results = checks.map(([prop, actual, expected]) => {
      return {
        property: prop,
        expected: expected,
        actual: actual,
        passed: actual === expected
      };
    });

    console.log('📋 VisualEngine 자가검사 결과:');
    results.forEach(r => {
      console.log(`  ${r.passed ? '✅' : '❌'} ${r.property}: ${actual} (기대: ${expected})`);
    });

    return results.every(r => r.passed);
  }
}

// 🔧 모듈 내보내기
export { VisualEngine, PALETTE };

// UMD 포맷 — 브라우저 호환성
if (typeof window !== 'undefined') {
  window.VisualEngine = VisualEngine;
}

/**
 * 데모 테스트 — 개발 환경용
 */
if (process.env.NODE_ENV === 'development' && typeof require !== 'undefined') {
  const demo = () => {
    console.log('🧪 VisualEngine Demo Test\n');
    
    // 가상 DOM 생성
    const mockDOM = document.createElement('div');
    mockDOM.id = 'critical-red-container';
    document.body.appendChild(mockDOM);

    const engine = new VisualEngine({ targetSelector: '#critical-red-container' });
    engine.connect();
    
    // 테스트 데이터로 업데이트
    const testData = {
      current: {
        value: 35,
        label: '35.0%',
        color: '#DC2626',
        icon: '🟠'
      },
      thresholds: [],
      levelLabel: 'CRITICAL'
    };
    
    engine.update(testData);
    
    // 스타일 검사
    const passed = engine.selfCheck();
    console.log(`\n✅ 데모 테스트 완료 — 결과: ${passed ? '통과' : '실패'}\n`);
    
    return passed;
  };

  if (typeof module !== 'undefined') {
    module.exports = VisualEngine;
    demo();
  }
}