import React, {useMemo, useState, useEffect} from 'react';
import {createRoot} from 'react-dom/client';
import {
  LayoutDashboard, Store, ArrowLeftRight, ShieldAlert, BrainCircuit,
  FileText, Search, Bell, ChevronDown, TrendingUp, TrendingDown,
  WalletCards, Activity, MapPin, CalendarDays, CircleCheck, TriangleAlert,
  X, Menu, RefreshCw, Download, ArrowUpRight, User, Check,
  SlidersHorizontal, ShieldCheck
} from 'lucide-react';
import './styles.css';
import {
  fetchVendors, fetchVendorTransactions, fetchFraudAnalysis,
  fetchAssessmentReport, runAssessment,
  fetchAAConsentStatus
} from './api/client';



const fallbackVendors = [
  {id:'VND-1042',vendor_id:'VND-1042',name:'Ramesh Tea & Snacks',vendor_name:'Ramesh Tea & Snacks',type:'Food & Beverage',business_type:'Food & Beverage',city:'Vellore',score:830,credit_score:830,status:'Excellent',rating:'Excellent',risk:'Low',trust:91,behavioral_trust:91,spv:0.86,tsci:0.89,mcs:0.83,resilience:0.96,svps:0.04,volume:184200,growth:12.8,days:27,transactions:1438,customers:214},
  {id:'VND-1178',vendor_id:'VND-1178',name:'Lakshmi Vegetable Stall',vendor_name:'Lakshmi Vegetable Stall',type:'Fresh Produce',business_type:'Fresh Produce',city:'Katpadi',score:774,credit_score:774,status:'Very Good',rating:'Very Good',risk:'Moderate',trust:82,behavioral_trust:82,spv:0.78,tsci:0.81,mcs:0.76,resilience:0.91,svps:0.11,volume:132600,growth:8.4,days:25,transactions:1192,customers:186},
  {id:'VND-1291',vendor_id:'VND-1291',name:'Arun Mobile Repairs',vendor_name:'Arun Mobile Repairs',type:'Electronics Repair',business_type:'Electronics Repair',city:'Vellore',score:683,credit_score:683,status:'Fair',rating:'Fair',risk:'Elevated',trust:68,behavioral_trust:68,spv:0.63,tsci:0.69,mcs:0.58,resilience:0.84,svps:0.22,volume:98600,growth:3.1,days:21,transactions:806,customers:97}
];

function App() {
  const [vendors, setVendors] = useState(fallbackVendors);
  const [selected, setSelected] = useState(fallbackVendors[0]);
  const [page, setPage] = useState('Dashboard');
  const [menu, setMenu] = useState(false);
  const [search, setSearch] = useState('');
  const [assessment, setAssessment] = useState(false);
  const [loading, setLoading] = useState(false);
  const [backendOnline, setBackendOnline] = useState(false);
  const [txList, setTxList] = useState([]);
  const [fraudData, setFraudData] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [aaConsent, setAaConsent] = useState(null);
  const [aaModalOpen, setAaModalOpen] = useState(false);
  const [txFilter, setTxFilter] = useState('All');
  const [notifOpen, setNotifOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [searchFocused, setSearchFocused] = useState(false);
  const [activeRole, setActiveRole] = useState('Credit Analyst');
  const [toastMessage, setToastMessage] = useState(null);
  const [notifications, setNotifications] = useState([
    { id: 1, type: 'warn', title: 'Suspicious Velocity Spike', text: 'Arun Mobile Repairs (VND-1002) observed with elevated ₹12K night transfers.', time: '5m ago', vendorId: 'VND-1002', unread: true },
    { id: 2, type: 'good', title: 'High Credit Trust Rating', text: 'Ramesh Tea & Snacks scored 824/900 (Strong Approval) based on 86% SPV.', time: '22m ago', vendorId: 'VND-1000', unread: true },
    { id: 3, type: 'good', title: 'Seasonal Shock Absorbed', text: 'Lakshmi Vegetable Stall showed 91% STL seasonal resilience across monsoons.', time: '1h ago', vendorId: 'VND-1001', unread: true },
    { id: 4, type: 'info', title: 'Graph Cycle Verification', text: 'No circular fund cycles found across current active counterparty network.', time: '3h ago', vendorId: null, unread: false }
  ]);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleNotifClick = (n) => {
    if (n.vendorId) {
      const match = vendors.find(v => (v.id || v.vendor_id) === n.vendorId);
      if (match) {
        setSelected(match);
        go(n.type === 'warn' ? 'Risk & Fraud' : 'Assessment Report');
      }
    }
    setNotifications(prev => prev.map(item => item.id === n.id ? { ...item, unread: false } : item));
    setNotifOpen(false);
  };

  const searchMatches = search.trim().length > 0 
    ? vendors.filter(v => ((v.name || v.vendor_name) + (v.id || v.vendor_id) + v.city).toLowerCase().includes(search.toLowerCase())).slice(0, 6)
    : [];

  const unreadCount = notifications.filter(n => n.unread).length;

  const loadInitialVendors = async () => {
    try {
      const list = await fetchVendors();
      if (list && list.length > 0) {
        const formatted = list.map(v => ({
          ...v,
          id: v.vendor_id,
          name: v.vendor_name,
          type: v.business_type,
          score: v.credit_score,
          status: v.rating,
          trust: v.behavioral_trust
        }));
        setVendors(formatted);
        setSelected(formatted[0]);
        setBackendOnline(true);
      }
    } catch (err) { setBackendOnline(false); }
  };

  useEffect(() => { loadInitialVendors(); }, []);

  useEffect(() => {
    if (!selected) return;
    const vId = selected.id || selected.vendor_id;
    async function loadDetails() {
      try { const txs = await fetchVendorTransactions(vId); setTxList(txs); } catch(e){ setTxList([]); }
      try { const fr = await fetchFraudAnalysis(vId); setFraudData(fr); } catch(e){ setFraudData(null); }
      try { const rep = await fetchAssessmentReport(vId); setReportData(rep); } catch(e){ setReportData(null); }
      try { const aa = await fetchAAConsentStatus(vId); setAaConsent(aa); } catch(e){ setAaConsent(null); }
    }
    loadDetails();
  }, [selected]);

  const filtered = useMemo(() => vendors.filter(v => ((v.name || v.vendor_name) + (v.id || v.vendor_id) + v.city).toLowerCase().includes(search.toLowerCase())), [vendors, search]);
  const go = p => { setPage(p); setMenu(false); setNotifOpen(false); setUserMenuOpen(false); setSearchFocused(false); };

  const handleRunAssessment = async () => {
    const vId = selected.id || selected.vendor_id;
    setLoading(true);
    try {
      const rep = await runAssessment(vId);
      setReportData(rep);
      setSelected(prev => ({ ...prev, score: rep.credit_score, trust: rep.behavioral_trust, status: rep.rating }));
    } catch(err) {} finally { setLoading(false); setAssessment(true); }
  };

  return (
    <div className='app'>
      <aside className={menu ? 'sidebar open' : 'sidebar'}>
        <div className='brand'><div className='brandmark'>P</div><div><b>Pehchaan</b><span>Credit Engine</span></div><button className='close' onClick={() => setMenu(false)}><X size={18}/></button></div>
        <div className='section-label'>WORKSPACE</div>
        {[
          ['Dashboard', LayoutDashboard],
          ['Vendors', Store],
          ['Transactions', ArrowLeftRight],
          ['Behavioral Analysis', BrainCircuit],
          ['Risk & Fraud', ShieldAlert],
          ['Assessment Report', FileText]
        ].map(([n, I]) => (
          <button className={page === n ? 'nav active' : 'nav'} onClick={() => go(n)} key={n}><I size={18}/><span>{n}</span></button>
        ))}

        <div className='sidebar-bottom'><div className='model'><div className='pulse' style={{ background: backendOnline ? '#53c7ae' : '#e3a35b' }}></div><div><b>Engine status</b><span>{backendOnline ? 'Live API • Connected' : 'Prototype • Ready'}</span></div></div><small>Behavioral Trust Engine<br/>v0.1 • Review 2</small></div>
      </aside>
      <main className='main'>
        <header>
          <button className='hamb' onClick={() => setMenu(true)}><Menu/></button>
          <div className='crumb'>
            <b className='clickable' onClick={() => go('Dashboard')}>Pehchaan Credit</b>
            <span>/</span>
            {page}
          </div>
          <div className='head-actions'>
            <div className='search-wrapper'>
              <div className='search'>
                <Search size={17}/>
                <input 
                  value={search} 
                  onChange={e => { setSearch(e.target.value); setSearchFocused(true); }}
                  onFocus={() => setSearchFocused(true)}
                  placeholder='Search vendor or ID'
                />
                {search && (
                  <button 
                    style={{border: 0, background: 'none', cursor: 'pointer', color: '#8fa0ad', padding: 0}}
                    onClick={() => setSearch('')}
                  >
                    <X size={14}/>
                  </button>
                )}
              </div>
              {searchFocused && search.trim().length > 0 && (
                <div className='search-dropdown'>
                  {searchMatches.length > 0 ? (
                    searchMatches.map(v => (
                      <button
                        key={v.id || v.vendor_id}
                        className='search-dropdown-item'
                        onClick={() => {
                          setSelected(v);
                          setSearch('');
                          setSearchFocused(false);
                          go('Assessment Report');
                        }}
                      >
                        <div className='vavatar' style={{width: 28, height: 28, fontSize: 9}}>
                          {(v.name || v.vendor_name).split(' ').map(x => x[0]).slice(0, 2).join('')}
                        </div>
                        <div>
                          <b>{v.name || v.vendor_name}</b>
                          <span>{(v.id || v.vendor_id)} • {(v.type || v.business_type)} • {v.city}</span>
                        </div>
                        <em>{v.score || v.credit_score}</em>
                      </button>
                    ))
                  ) : (
                    <div style={{padding: '16px', fontSize: 11, color: 'var(--muted)', textAlign: 'center'}}>
                      No vendors found matching "{search}"
                    </div>
                  )}
                </div>
              )}
            </div>

            <button 
              className='aa-header-badge' 
              title='View RBI Account Aggregator Consent Artifact'
              onClick={() => setAaModalOpen(true)}
            >
              <ShieldCheck size={14}/>
              <span>RBI AA: Verified</span>
            </button>

            <button 
              className={'btn-icon-interactive ' + (notifOpen ? 'active' : '')} 
              title='Underwriting Alerts'
              onClick={() => { setNotifOpen(!notifOpen); setUserMenuOpen(false); setSearchFocused(false); }}
            >
              <Bell size={18}/>
              {unreadCount > 0 && <i className='badge-dot'></i>}
            </button>

            {notifOpen && (
              <div className='popover-container notif-popover'>
                <div className='notif-popover-head'>
                  <b>Underwriting Alerts ({unreadCount})</b>
                  <button onClick={() => setNotifications(prev => prev.map(n => ({...n, unread: false})))}>
                    Mark all read
                  </button>
                </div>
                <div className='notif-popover-list'>
                  {notifications.map(n => (
                    <div 
                      key={n.id} 
                      className={'notif-popover-item ' + (n.unread ? 'unread' : '')}
                      onClick={() => handleNotifClick(n)}
                    >
                      <div className={'notif-bubble ' + n.type}>
                        {n.type === 'warn' ? <ShieldAlert size={14}/> : <CircleCheck size={14}/>}
                      </div>
                      <div className='notif-content'>
                        <b>{n.title}</b>
                        <p>{n.text}</p>
                        <small>{n.time}</small>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <button 
              className={'user-btn ' + (userMenuOpen ? 'active' : '')}
              onClick={() => { setUserMenuOpen(!userMenuOpen); setNotifOpen(false); setSearchFocused(false); }}
            >
              <div className='avatar'>SG</div>
              <div>
                <b>{activeRole}</b>
                <span>Review workspace</span>
              </div>
              <ChevronDown size={16} style={{transform: userMenuOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.15s'}}/>
            </button>

            {userMenuOpen && (
              <div className='popover-container user-popover'>
                <div className='user-popover-info'>
                  <b>Siddharth Gautam</b>
                  <span>Senior Credit Underwriter</span>
                  <em>{activeRole}</em>
                </div>
                <div className='user-popover-actions'>
                  <span style={{fontSize: 9, fontWeight: 700, letterSpacing: '0.08em', color: '#91a1ad', padding: '6px 12px', display: 'block'}}>
                    WORKSPACE ROLE
                  </span>
                  {['Credit Analyst', 'Risk & Compliance Officer', 'Field Audit Specialist'].map(r => (
                    <button 
                      key={r} 
                      className={'user-popover-btn ' + (activeRole === r ? 'active' : '')}
                      onClick={() => {
                        setActiveRole(r);
                        showToast(`Active role set to: ${r}`);
                        setUserMenuOpen(false);
                      }}
                    >
                      {activeRole === r ? <Check size={14}/> : <User size={14}/>}
                      <span>{r}</span>
                    </button>
                  ))}
                  <div style={{height: 1, background: '#edf2f5', margin: '6px 0'}}></div>
                  <button 
                    className='user-popover-btn'
                    onClick={() => {
                      showToast('XGBoost Model Status: Online • Test R²: 0.8763 • 1,000 Vendors Indexed');
                      setUserMenuOpen(false);
                    }}
                  >
                    <BrainCircuit size={14}/>
                    <span>Engine Diagnostics</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </header>
        {(notifOpen || userMenuOpen || searchFocused) && (
          <div className='popover-backdrop' onClick={() => { setNotifOpen(false); setUserMenuOpen(false); setSearchFocused(false); }}/>
        )}
        {toastMessage && (
          <div style={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            background: '#102333',
            color: '#fff',
            padding: '12px 18px',
            borderRadius: '8px',
            boxShadow: '0 8px 24px rgba(0,0,0,0.25)',
            zIndex: 200,
            font: "600 12px 'DM Sans', sans-serif",
            display: 'flex',
            alignItems: 'center',
            gap: 10
          }}>
            <CircleCheck size={16} style={{color: 'var(--teal)'}}/>
            <span>{toastMessage}</span>
          </div>
        )}
        <div className='content'>
          {page === 'Dashboard' && <Dashboard selected={selected} setSelected={setSelected} vendors={vendors} filtered={filtered} setAssessment={handleRunAssessment} loading={loading} txList={txList} onRefresh={loadInitialVendors}/>}
          {page === 'Vendors' && <Vendors selected={selected} setSelected={setSelected} filtered={filtered} go={go}/>}
          {page === 'Transactions' && <Transactions selected={selected} txList={txList} filter={txFilter} setFilter={setTxFilter}/>}
          {page === 'Behavioral Analysis' && <Behavioral selected={selected}/>}
          {page === 'Risk & Fraud' && <Risk selected={selected} fraudData={fraudData}/>}
          {page === 'Assessment Report' && <Report selected={selected} reportData={reportData}/>}
        </div>

      </main>
      {assessment && <div className='modal-bg' onClick={() => setAssessment(false)}><div className='modal' onClick={e => e.stopPropagation()}><div className='modal-icon'><CircleCheck/></div><h2>Assessment completed</h2><p>The prototype assessment has refreshed the behavioral indicators for <b>{selected.name || selected.vendor_name}</b>.</p><div className='modal-score'><span>Behavioral Trust Score</span><b>{selected.trust || selected.behavioral_trust}/100</b></div><button className='primary' onClick={() => { setAssessment(false); setPage('Assessment Report'); }}>Open report</button></div></div>}
      {aaModalOpen && (
        <div className='aa-modal-overlay' onClick={() => setAaModalOpen(false)}>
          <div className='aa-modal-card' onClick={e => e.stopPropagation()}>
            <div className='aa-modal-head'>
              <b><ShieldCheck size={18}/> RBI Account Aggregator Consent Artifact</b>
              <button style={{border:0, background:'transparent', color:'#fff', cursor:'pointer'}} onClick={() => setAaModalOpen(false)}><X size={18}/></button>
            </div>
            <div className='aa-modal-body'>
              <div className='aa-field-row'><span>Consent ID</span><b>{aaConsent?.consent_id || 'AA-CONSENT-VND-9821'}</b></div>
              <div className='aa-field-row'><span>Consent Status</span><span className='provenance-tag verified'>ACTIVE • RBI COMPLIANT</span></div>
              <div className='aa-field-row'><span>Financial Info Provider (FIP)</span><b>{aaConsent?.fip_id || 'State Bank of India (SBI-FIP-01)'}</b></div>
              <div className='aa-field-row'><span>Financial Info User (FIU)</span><b>PEHCHAAN_CREDIT_FIU</b></div>
              <div className='aa-field-row'><span>Verified Account Mask</span><b>{aaConsent?.account_mask || 'XXXXXXXX9021'}</b></div>
              <div className='aa-field-row'><span>Average Daily Balance (12m)</span><b style={{color:'var(--teal)'}}>₹{(aaConsent?.avg_daily_balance || 18450).toLocaleString()}</b></div>
              <div className='aa-field-row'><span>Cheque Bounces (180d)</span><b style={{color:'#102333'}}>0 (Zero Default)</b></div>
              <div className='aa-field-row'><span>Data Fetch Frequency</span><b>DAILY RECURRENT</b></div>
              <div className='aa-field-row'><span>Consent Validity</span><b>365 Days (Valid to Nov 2026)</b></div>
              <div style={{marginTop: 16, textAlign: 'right'}}>
                <button className='btn-dark' onClick={() => setAaModalOpen(false)}>Close Inspector</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
function Top({eyebrow, title, sub, children}) {
  return <div className='top'><div><div className='eyebrow'>{eyebrow}</div><h1>{title}</h1><p>{sub}</p></div>{children}</div>;
}
function ScoreRing({score}) {
  return <div className='ring' style={{'--p': (score || 70) * 3.6 + 'deg'}}><div><b>{score || 70}</b><span>/ 100</span></div></div>;
}
function Dashboard({selected, setSelected, vendors, filtered, setAssessment, loading, txList, onRefresh}) {
  const displayTx = txList && txList.length > 0 ? txList.slice(0, 4).map(t => [
    t.transaction_id, t.payment_channel, t.transaction_type, '₹' + Number(t.amount).toLocaleString(), t.timestamp, t.status || 'Normal'
  ]) : [
    ['TXN-89321','UPI','Customer Sale','₹2,450','02 Sep 2026, 10:42 AM','Normal'],
    ['TXN-89318','UPI','Supplier Payment','₹8,200','02 Sep 2026, 09:18 AM','Normal'],
    ['TXN-89305','UPI','Customer Sale','₹1,280','01 Sep 2026, 07:31 PM','Normal'],
    ['TXN-89277','UPI','Transfer','₹12,000','01 Sep 2026, 11:58 PM','Review']
  ];
  return <>
    <Top eyebrow='LENDER WORKSPACE' title='Behavioral Trust Dashboard' sub='Assess informal businesses using transaction behaviour, business rhythm and fraud-aware signals.'>
      <div className='actions-cluster'>
        <button className='btn-outline' onClick={onRefresh}><RefreshCw size={14}/> Refresh</button>
        <button className='btn-dark' onClick={setAssessment} disabled={loading}><BrainCircuit size={16}/> {loading ? 'Evaluating...' : 'Run Assessment'}</button>
      </div>
    </Top>
    <div className='vendorbar'><div><span className='label'>SELECTED VENDOR</span><select value={selected.id || selected.vendor_id} onChange={e => setSelected(vendors.find(v => (v.id || v.vendor_id) === e.target.value))}>{vendors.map(v => <option key={v.id || v.vendor_id} value={v.id || v.vendor_id}>{v.name || v.vendor_name} • {v.id || v.vendor_id}</option>)}</select></div><div className='vendor-mini'><div className='mini-avatar'>{(selected.name || selected.vendor_name).split(' ').map(x => x[0]).slice(0, 2).join('')}</div><div><b>{selected.type || selected.business_type}</b><span><MapPin size={13}/> {selected.city}</span></div></div></div>
    <div className='cards'><Metric title='Behavioral Trust' value={selected.trust || selected.behavioral_trust} suffix='/100' note='Overall behavioural quality' icon={<BrainCircuit/>} trend='+4.2%'/><Metric title='Credit Score' value={selected.score || selected.credit_score} note={selected.status || selected.rating} icon={<WalletCards/>} trend='Calculated'/><Metric title='Fraud Risk' value={Math.round((selected.svps || 0.04) * 100)} suffix='%' note='Synthetic volume penalty' icon={<ShieldAlert/>} trend={selected.risk}/><Metric title='Business Growth' value={selected.growth || 12.8} suffix='%' note='30-day business trend' icon={<TrendingUp/>} trend='Positive'/></div>
    <div className='grid2'><section className='panel'><div className='panel-head'><div><h3>Behavioral signal profile</h3><p>Evidence entering the assessment pipeline</p></div><span className='badge good'><CircleCheck size={13}/> {selected.status || selected.rating}</span></div><Signal label='Supplier Payment Velocity' code='SPV • 15%' value={selected.spv || 0.86} desc='Regular supplier payments indicate genuine business activity.'/><Signal label='Transaction Stability & Consistency' code='TSCI • 15%' value={selected.tsci || 0.89} desc='Measures stable temporal and business rhythm.'/><Signal label='Merchant Customer Score' code='MCS • 15%' value={selected.mcs || 0.83} desc='Customer diversity, recurrence and reciprocity.'/><Signal label='Seasonal Resilience' code='R • 10%' value={selected.resilience || 0.96} desc='Performance against expected seasonal income.'/></section><section className='panel'><div className='panel-head'><div><h3>Trust score composition</h3><p>Explainable view for lender review</p></div><span className='badge'>Live prototype</span></div><div className='score-wrap'><ScoreRing score={selected.trust || selected.behavioral_trust}/><div className='score-copy'><b>{selected.status || selected.rating}</b><p>Strong behavioural evidence with low fraud exposure.</p><div className='legend'><span><i></i> Business behaviour</span><span><i></i> Risk adjustment</span></div></div></div><div className='explain'><b>Why this score?</b><p>Consistent transactions and supplier payments support trust. Suspicious volume is considered before the final assessment.</p></div></section></div>
    <section className='panel'><div className='panel-head'><div><h3>Recent transaction activity</h3><p>{(selected.transactions || 1438).toLocaleString()} transactions observed • {selected.days || 27} active days</p></div><button className='textbtn'>View all →</button></div><TxTable rows={displayTx}/></section>
  </>;
}
function Metric({title, value, suffix='', note, icon, trend}) {
  return <div className='metric'><div className='metric-top'><div className='metric-icon'>{icon}</div><span>{trend}</span></div><h3>{typeof value === 'number' && value % 1 !== 0 ? value.toFixed(1) : value}<small>{suffix}</small></h3><b>{title}</b><p>{note}</p></div>;
}
function Signal({label, code, value, desc}) {
  const pct = Math.round((value || 0) * 100);
  return <div className='signal'><div className='signal-line'><div><b>{label}</b> <span>{code}</span></div><strong>{pct}%</strong></div><div className='bar'><i style={{width: pct + '%'}}></i></div><p>{desc}</p></div>;
}
function Vendors({selected, setSelected, filtered, go}) {
  const totalVendors = filtered.length;
  const avgTrust = Math.round(filtered.reduce((acc, v) => acc + (v.trust || v.behavioral_trust || 75), 0) / (totalVendors || 1));
  const lowRiskCount = filtered.filter(v => (v.risk || 'Low') === 'Low').length;
  const reviewCount = filtered.filter(v => (v.risk || 'Low') !== 'Low').length;

  return <>
    <Top eyebrow='VENDOR PORTFOLIO' title='Vendor Assessment Workspace' sub='Review transaction behaviour and credit readiness across informal businesses.'/>
    <div className='cards'>
      <Metric title='Total Vendors' value={totalVendors} note='Current workspace' icon={<Store/>} trend='Portfolio'/>
      <Metric title='Average Trust' value={avgTrust} suffix='/100' note='Behavioural evidence' icon={<BrainCircuit/>} trend='Portfolio'/>
      <Metric title='Low Risk' value={lowRiskCount} note='Lower fraud exposure' icon={<ShieldAlert/>} trend='Healthy'/>
      <Metric title='Needs Review' value={reviewCount} note='Risk indicators present' icon={<Activity/>} trend='Monitor'/>
    </div>
    <section className='panel'>
      <div className='panel-head'>
        <div><h3>Vendor portfolio</h3><p>Select a vendor to inspect its behavioural assessment.</p></div>
        <button className='btn-outline'><Download size={14}/> Export</button>
      </div>
      <div className='vendor-table'>
        {filtered.map(v => (
          <div 
            key={v.id || v.vendor_id} 
            className={(v.id || v.vendor_id) === (selected.id || selected.vendor_id) ? 'vrow selected' : 'vrow'} 
            onClick={() => setSelected(v)}
            role='button'
            tabIndex={0}
          >
            <div className='vavatar'>{(v.name || v.vendor_name).split(' ').map(x => x[0]).slice(0, 2).join('')}</div>
            <div><b>{v.name || v.vendor_name}</b><span>{(v.id || v.vendor_id)} • {v.type || v.business_type}</span><span className='muted'><MapPin size={10}/> {v.city}</span></div>
            <div><span className='muted'>Trust</span><b>{v.trust || v.behavioral_trust}/100</b></div>
            <div><span className='muted'>Credit</span><b>{v.score || v.credit_score}</b></div>
            <div><span className='muted'>Activity</span><b>{v.days || 27}/30</b></div>
            <div><span className={'badge ' + (v.risk === 'Low' ? 'good' : 'warn')}>{v.risk}</span></div>
            <button 
              type='button' 
              className='vrow-arrow-btn' 
              title='Open Assessment Report'
              onClick={(e) => {
                e.stopPropagation();
                setSelected(v);
                go('Assessment Report');
              }}
            >
              <ArrowUpRight size={16}/>
            </button>
          </div>
        ))}
      </div>
    </section>
    <div className='inspector-panel'>
      <div className='inspector-head'>
        <div className='inspector-vendor'>
          <div className='mini-avatar' style={{width: 44, height: 44, fontSize: 13}}>{(selected.name || selected.vendor_name).split(' ').map(x => x[0]).slice(0, 2).join('')}</div>
          <div><span className='label'>SELECTED VENDOR</span><h2 style={{margin: '4px 0 2px', font: '800 20px Manrope'}}>{selected.name || selected.vendor_name}</h2><p style={{margin: 0, fontSize: 11, color: '#788794'}}>{selected.id || selected.vendor_id} • {selected.type || selected.business_type} • {selected.city}</p></div>
        </div>
        <div className='inspector-score'><span>Credit Score</span><b>{selected.score || selected.credit_score}</b><em>{selected.status || selected.rating}</em></div>
      </div>
      <div className='inspector-grid'>
        <div className='inspector-kpi'><Activity size={14} style={{color: 'var(--teal)'}}/><span>Behavioral Trust</span><b>{selected.trust || selected.behavioral_trust}/100</b><small style={{fontSize: 9, color: 'var(--muted)'}}>Overall evidence</small></div>
        <div className='inspector-kpi'><ArrowLeftRight size={14} style={{color: 'var(--teal)'}}/><span>Transactions</span><b>{(selected.transactions || 1438).toLocaleString()}</b><small style={{fontSize: 9, color: 'var(--muted)'}}>Observed activity</small></div>
        <div className='inspector-kpi'><Store size={14} style={{color: 'var(--teal)'}}/><span>Customers</span><b>{selected.customers || 214}</b><small style={{fontSize: 9, color: 'var(--muted)'}}>Distinct customers</small></div>
        <div className='inspector-kpi'><TrendingUp size={14} style={{color: 'var(--teal)'}}/><span>Growth</span><b>+{selected.growth || 12.8}%</b><small style={{fontSize: 9, color: 'var(--muted)'}}>30-day trend</small></div>
      </div>
      <div className='inspector-actions'>
        <button className='btn-outline' onClick={() => go('Transactions')}><ArrowLeftRight size={14}/> View Transactions</button>
        <button className='btn-outline' onClick={() => go('Risk & Fraud')}><ShieldAlert size={14}/> Review Risk</button>
        <button className='btn-dark' onClick={() => go('Assessment Report')}><FileText size={14}/> Open Assessment Report <ArrowUpRight size={14}/></button>
      </div>
    </div>
  </>;
}
function Transactions({selected, txList, filter, setFilter}) {
  const rawRows = txList && txList.length > 0 ? txList.map(t => [
    t.transaction_id, t.payment_channel, t.transaction_type, '₹' + Number(t.amount).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}), t.timestamp, t.status || 'Normal'
  ]) : [
    ['TXN-89321','UPI','Customer Sale','₹2,450.00','02 Sep 2026, 10:42 AM','Normal'],
    ['TXN-89318','UPI','Supplier Payment','₹8,200.00','02 Sep 2026, 09:18 AM','Normal'],
    ['TXN-89305','UPI','Customer Sale','₹1,280.00','01 Sep 2026, 07:31 PM','Normal'],
    ['TXN-89277','UPI','Transfer','₹12,000.00','01 Sep 2026, 11:58 PM','Review'],
    ['TXN-89241','UPI','Customer Sale','₹3,150.00','01 Sep 2026, 01:16 PM','Normal'],
    ['TXN-89215','UPI','Supplier Payment','₹6,500.00','31 Aug 2026, 09:07 AM','Normal'],
    ['TXN-89193','UPI','Customer Sale','₹1,850.00','31 Aug 2026, 05:21 PM','Normal']
  ];

  const countAll = rawRows.length;
  const countNormal = rawRows.filter(r => String(r[5]).toLowerCase() === 'normal').length;
  const countReview = rawRows.filter(r => String(r[5]).toLowerCase() === 'review').length;

  const filteredRows = filter === 'All' 
    ? rawRows 
    : rawRows.filter(r => String(r[5]).toLowerCase() === filter.toLowerCase());

  const handleExport = () => {
    const csvContent = 'data:text/csv;charset=utf-8,' 
      + ['ID,CHANNEL,TYPE,AMOUNT,TIME,STATUS', ...filteredRows.map(r => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `${selected.id || selected.vendor_id}_transactions_${filter.toLowerCase()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return <>
    <Top eyebrow='TRANSACTION INTELLIGENCE' title='Transaction Activity' sub={'Transaction evidence for ' + (selected.name || selected.vendor_name) + ' (' + (selected.id || selected.vendor_id) + ').'}>
      <button className='btn-outline' onClick={handleExport}><Download size={14}/> Export</button>
    </Top>
    <div className='cards'>
      <Metric title='Total Volume' value={'₹' + (((selected.volume || 184200)) / 1000).toFixed(1) + 'K'} note='Observed transaction volume' icon={<WalletCards/>} trend='30 days'/>
      <Metric title='Active Days' value={selected.days || 27} suffix='/30' note='Business operating days' icon={<CalendarDays/>} trend='Regular'/>
      <Metric title='Customers' value={selected.customers || 214} note='Distinct customer base' icon={<Store/>} trend='Diverse'/>
      <Metric title='Transactions' value={(selected.transactions || 1438).toLocaleString()} note='Observed transactions' icon={<Activity/>} trend='Stable'/>
    </div>
    <section className='panel'>
      <div className='panel-head'>
        <div><h3>Transaction ledger</h3><p>Verified digital payment activity</p></div>
        <div className='filter-tabs'>
          {[
            { id: 'All', label: `All (${countAll})` },
            { id: 'Normal', label: `Normal (${countNormal})` },
            { id: 'Review', label: `Review (${countReview})` }
          ].map(tab => (
            <button key={tab.id} className={'filter-tab ' + (filter.toLowerCase() === tab.id.toLowerCase() ? 'active' : '')} onClick={() => setFilter(tab.id)}>
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      <TxTable rows={filteredRows} filter={filter}/>
    </section>
  </>;
}
function TxTable({rows, filter = 'All'}) {
  return (
    <div className='table'>
      <div className='tr th'>
        <span>ID</span>
        <span>CHANNEL</span>
        <span>TYPE</span>
        <span>AMOUNT</span>
        <span>TIME</span>
        <span>STATUS</span>
      </div>
      {rows.length > 0 ? (
        rows.map(r => (
          <div className='tr' key={r[0]}>
            {r.map((x, i) => (
              <span key={i}>
                {i === 5 ? (
                  <em className={String(x).toLowerCase() === 'normal' ? 'ok' : 'review'}>{x}</em>
                ) : (
                  x
                )}
              </span>
            ))}
          </div>
        ))
      ) : (
        <div style={{padding: '36px 16px', textAlign: 'center', color: 'var(--muted)', fontSize: 13}}>
          No transactions found for filter "<b>{filter}</b>" for this vendor.
        </div>
      )}
    </div>
  );
}
function Behavioral({selected}) {
  return <>
    <Top eyebrow='BEHAVIORAL ANALYSIS' title='Behavioral Signal Analysis' sub='Detailed behavioural evidence supporting the credit assessment.'/>
    <div className='analysis-grid'>
      <section className='panel'>
        <div className='panel-head'>
          <div><h3>Core behavioral indices</h3><p>Project-defined assessment signals</p></div>
          <span className='badge good'><CircleCheck size={13}/> Signals ready</span>
        </div>
        <Signal label='Supplier Payment Velocity' code='SPV • 15%' value={selected.spv || 0.86} desc='Supplier Payments ÷ Total Outbound. Regular supplier payments indicate genuine stock purchasing and business activity.'/>
        <Signal label='Transaction Stability & Consistency' code='TSCI • 15%' value={selected.tsci || 0.89} desc='Combines temporal stability, peak-hour behaviour and available geographical consistency.'/>
        <Signal label='Merchant Customer Score' code='MCS • 15%' value={selected.mcs || 0.83} desc='Customer diversity + healthy recurrence − reciprocal transaction behaviour.'/>
        <Signal label='Seasonal Resilience' code='R • 10%' value={selected.resilience || 0.96} desc='Measures actual business performance relative to expected seasonal income.'/>
      </section>
      <section className='panel'>
        <div className='panel-head'><div><h3>Business profile</h3><p>Observed operating behaviour</p></div></div>
        <div className='bigstat'>
          <span>Monthly transaction volume</span>
          <b style={{font: '800 36px Manrope'}}>₹{(selected.volume || 184200).toLocaleString()}</b>
          <small><TrendingUp size={14}/> +{selected.growth || 12.8}% growth</small>
        </div>
        <div className='facts'>
          <div><span>Active days</span><b>{selected.days || 27}/30</b></div>
          <div><span>Transactions/day</span><b>{Math.round((selected.transactions || 1438) / (selected.days || 27))}</b></div>
          <div><span>Customers</span><b>{selected.customers || 214}</b></div>
        </div>
        <div className='callout'>
          <CircleCheck/>
          <div>
            <b>Behavioral evidence captured</b>
            <p>These indicators are passed into the credit-quality assessment stage.</p>
          </div>
        </div>
      </section>
    </div>
    <div className='panel' style={{marginTop: 20}}>
      <div className='panel-head'><div><h3>What each signal tells the lender</h3><p>Human-readable interpretation of the behavioural indicators</p></div></div>
      <div className='explain-grid'>
        <div className='explain-card'><CircleCheck/><div><b>Supplier Payment Velocity</b><p>A healthy supplier-payment pattern supports the interpretation that transaction volume is connected to genuine business operations.</p></div></div>
        <div className='explain-card'><CircleCheck/><div><b>Transaction Stability</b><p>Consistent business rhythm helps distinguish regular commercial activity from irregular transaction behaviour.</p></div></div>
        <div className='explain-card'><CircleCheck/><div><b>Customer Quality</b><p>A diverse customer base with healthy recurrence provides stronger evidence than reciprocal or concentrated transfers.</p></div></div>
        <div className='explain-card'><CircleCheck/><div><b>Seasonal Resilience</b><p>The vendor is evaluated against expected seasonal performance instead of treating every temporary decline as a weakness.</p></div></div>
      </div>
    </div>
  </>;
}
function Risk({selected, fraudData}) {
  const svps = fraudData ? fraudData.svps : (selected.svps || 0.04);
  const svpsPct = Math.round(svps * 100);
  const riskBand = fraudData ? fraudData.risk_band : (selected.risk || 'Low');
  const qBase = (selected.q_base || 0.892).toFixed(3);
  const qFinal = (selected.q_final || 0.883).toFixed(3);

  return <>
    <Top eyebrow='RISK & FRAUD' title='Risk & Fraud Monitor' sub='Fraud-aware assessment using suspicious-volume adjustment.'/>
    <div className='risk-hero'>
      <div>
        <span className='eyebrow'>SYNTHETIC VOLUME PENALTY SCORE</span>
        <h2>{svpsPct}%</h2>
        <p>Suspicious-volume estimate</p>
      </div>
      <div className='risk-meter'>
        <div className='bar'><i style={{width: svpsPct + '%'}}></i></div>
        <span>0% normal</span>
        <span>100% highly suspicious</span>
      </div>
    </div>
    <div className='grid2'>
      <section className='panel'>
        <div className='panel-head'>
          <div><h3>Fraud indicators</h3><p>Behavioural checks requiring review</p></div>
          <span className='badge good'>Low</span>
        </div>
        <Alert title='Repeated amount patterns' state='Low' text='Checks unusually repeated transaction amounts.'/>
        <Alert title='Sudden volume spikes' state='Low' text='Checks abnormal increases in transaction volume.'/>
        <Alert title='Reciprocal transfers' state='Low' text='Looks for back-and-forth transaction relationships.'/>
        <Alert title='Abnormal transaction timing' state='Low' text='Compares activity against the vendor normal business rhythm.'/>
      </section>
      <section className='panel'>
        <div className='panel-head'><div><h3>Risk-adjusted decision</h3><p>Effect on final credit quality</p></div></div>
        <div style={{textAlign: 'center', padding: '10px 0 16px'}}>
          <div className='decision-icon' style={{background: '#f0f5f7', color: '#3b5162'}}><ShieldAlert size={24}/></div>
          <h2 style={{font: '800 20px Manrope', margin: '10px 0 4px'}}>{riskBand} risk</h2>
          <p style={{fontSize: 10, color: '#7a8994', margin: 0}}>Suspicious transaction volume is incorporated into the final credit-quality calculation.</p>
        </div>
        <table className='risk-table'>
          <tbody>
            <tr><td>Q_base</td><td>{qBase}</td></tr>
            <tr><td>SVPS</td><td>{(svps).toFixed(2)}</td></tr>
            <tr><td>Q_final</td><td>{qFinal}</td></tr>
            <tr><td>Credit Score</td><td>{selected.score || selected.credit_score}</td></tr>
          </tbody>
        </table>
      </section>
    </div>
    <div className='card-banner'>
      <div className='panel-head'><div><h3>Fraud detection framework</h3><p>Prototype representation of the proposed fraud-aware pipeline</p></div></div>
      <div className='framework-grid'>
        <div className='framework-card'><ShieldAlert size={18}/><b>Rule Engine</b><p>Repeated amounts, excessive night activity, sudden spikes and low customer diversity.</p></div>
        <div className='framework-card'><Activity size={18}/><b>Isolation Forest</b><p>Identifies anomalous transaction behaviour that differs from the vendor normal pattern.</p></div>
        <div className='framework-card'><Store size={18}/><b>Graph Analysis</b><p>Represents accounts and transactions as networks to identify circular or collusive relationships.</p></div>
        <div className='framework-card'><CalendarDays size={18}/><b>Temporal Analysis</b><p>Analyses transaction timing and business rhythm to identify abnormal activity.</p></div>
      </div>
    </div>
  </>;
}
function Report({selected, reportData}) {
  const score = reportData ? reportData.credit_score : (selected.score || 830);
  const rating = reportData ? reportData.rating : (selected.status || 'Excellent');
  const trust = reportData ? reportData.behavioral_trust : (selected.trust || 91);
  const qBase = (selected.q_base || 0.892).toFixed(3);
  const qFinal = (selected.q_final || 0.883).toFixed(3);
  const svps = (selected.svps || 0.04).toFixed(2);

  const p10 = reportData?.p10_score || Math.round(score * 0.91);
  const p50 = reportData?.p50_score || score;
  const p90 = reportData?.p90_score || Math.round(score * 1.07);

  const waterfallItems = reportData?.waterfall?.waterfall_items || [
    { factor: 'Base Population Baseline', delta: 620, is_base: true, rationale: 'Median unbanked vendor credit baseline prior to alternate data' },
    { factor: 'Supplier Payment Velocity (SPV)', delta: 38, is_base: false, rationale: 'Consistent morning Mandi wholesale purchases and timely inventory restocking' },
    { factor: 'Temporal-Spatial Rhythm (TSCI)', delta: 21, is_base: false, rationale: 'Daily operating consistency and concentrated peak-hour transaction entropy' },
    { factor: 'Seasonality & Weather Resilience', delta: 18, is_base: false, rationale: 'Robust daily revenue retention during monsoon and festival fluctuations' },
    { factor: 'Merchant Customer Score (MCS)', delta: 14, is_base: false, rationale: 'Healthy customer diversity with repeat neighborhood patrons' },
    { factor: 'Synthetic Volume Penalty (SVPS)', delta: -11, is_base: false, rationale: 'Adjustment for counterparty concentration or circular payment patterns' }
  ];

  return <>
    <Top eyebrow='ASSESSMENT REPORT' title='Trust Assessment' sub={'Lender-ready assessment summary for ' + (selected.name || selected.vendor_name) + '.'}>
      <button className='btn-dark' onClick={() => window.print()}><Download size={14}/> Print / Export</button>
    </Top>
    <div className='report-head'>
      <div>
        <span className='label'>VENDOR</span>
        <h2>{selected.name || selected.vendor_name}</h2>
        <p>{selected.id || selected.vendor_id} • {selected.type || selected.business_type} • {selected.city}</p>
      </div>
      <div className='report-score'>
        <span>Credit Score</span>
        <b>{score}</b>
        <em>{rating}</em>
      </div>
    </div>
    <div className='cards'>
      <Metric title='Behavioral Trust' value={trust} suffix='/100' note='Overall behavioural evidence' icon={<BrainCircuit/>} trend='Strong'/>
      <Metric title='Base Quality' value={qBase} note='Before fraud adjustment' icon={<Activity/>} trend='Calculated'/>
      <Metric title='SVPS' value={Math.round(selected.svps * 100 || 4)} suffix='%' note='Synthetic volume penalty' icon={<ShieldAlert/>} trend='Low'/>
      <Metric title='Final Quality' value={qFinal} note='After risk adjustment' icon={<WalletCards/>} trend='Ready'/>
    </div>

    {/* Section 3: Quantile Risk Bands */}
    <div className='quantiles-grid'>
      <div className='quantile-card p10'>
        <div className='quantile-label'>P10 • Conservative (Monsoon Stress)</div>
        <div className='quantile-val'>{p10}</div>
        <div className='quantile-desc'>Worst-case revenue during severe weather disruption</div>
      </div>
      <div className='quantile-card p50'>
        <div className='quantile-label'>P50 • Expected (Median Operations)</div>
        <div className='quantile-val'>{p50}</div>
        <div className='quantile-desc'>Baseline daily cashflow under normal market rhythm</div>
      </div>
      <div className='quantile-card p90'>
        <div className='quantile-label'>P90 • Optimistic (Festival Surge)</div>
        <div className='quantile-val'>{p90}</div>
        <div className='quantile-desc'>Peak potential during Diwali / Pongal demand surge</div>
      </div>
    </div>

    {/* Section 3: Plain-Language SHAP Waterfall Attribution */}
    <div className='waterfall-box'>
      <div className='panel-head'>
        <div>
          <h3>Plain-Language SHAP Waterfall Attribution</h3>
          <p>Explainable point-by-point credit score breakdown</p>
        </div>
        <span className='badge good'>TreeSHAP</span>
      </div>
      <div className='waterfall-formula-bar'>
        Formula: {reportData?.waterfall?.formula_summary || `620 + 38 + 21 + 18 + 14 - 11 = ${score}`}
      </div>
      <div>
        {waterfallItems.map((item, idx) => (
          <div key={idx} className={'waterfall-item-row ' + (item.is_base ? 'base' : '')}>
            <div>
              <div className='waterfall-factor-title'>{item.factor}</div>
              <div className='waterfall-factor-rationale'>{item.rationale}</div>
            </div>
            <div>
              <span className={'waterfall-delta-pill ' + (item.is_base ? 'base' : (item.delta >= 0 ? 'pos' : 'neg'))}>
                {item.is_base ? item.delta : (item.delta >= 0 ? `+${item.delta}` : item.delta)} pts
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>

    <div className='grid2' style={{marginTop: 20}}>
      <section className='panel'>
        <div className='panel-head'><div><h3>Explainable decision</h3><p>Main factors influencing the result</p></div><span className='badge good'>Explainable</span></div>
        <div className='reason'><CircleCheck/><div><b>Supplier payment behaviour</b><p>SPV scored 86%, supporting genuine business activity.</p></div></div>
        <div className='reason'><CircleCheck/><div><b>Transaction consistency</b><p>TSCI scored 89%, indicating a stable operating rhythm.</p></div></div>
        <div className='reason'><CircleCheck/><div><b>Customer quality</b><p>MCS scored 83%, supporting customer-side evidence.</p></div></div>
        <div className='reason'><CircleCheck/><div><b>Fraud-aware adjustment</b><p>SVPS is 4%. Suspicious volume is penalized rather than automatically rejecting the vendor.</p></div></div>
      </section>
      <section className='panel'>
        <div className='panel-head'><div><h3>Score calculation</h3><p>Project-defined assessment values</p></div></div>
        <table className='score-table'>
          <tbody>
            <tr><td><span>Q_base</span><b>{qBase}</b></td><td><span>SVPS</span><b>{svps}</b></td></tr>
            <tr><td><span>Q_final</span><b>{qFinal}</b></td><td><span>Credit Score</span><b>{score}</b></td></tr>
            <tr><td><span>Rating</span><b>{rating}</b></td><td><span>Trust</span><b>{trust}/100</b></td></tr>
          </tbody>
        </table>
      </section>
    </div>
    <div className='card-banner' style={{marginTop: 20}}>
      <div className='panel-head'><div><h3>Assessment evidence</h3><p>Behavioural indicators used by the prototype</p></div></div>
      <div className='evidence-grid'>
        <div className='evidence-card'><div style={{display: 'flex', alignItems: 'center'}}><span className='evidence-num'>01</span><div><b>Supplier Payment Velocity</b><p style={{margin: 0, fontSize: 9.5, color: '#70818d'}}>Regular supplier payments support the presence of genuine business operations.</p></div></div><strong style={{font: '800 16px Manrope', color: '#102333'}}>86%</strong></div>
        <div className='evidence-card'><div style={{display: 'flex', alignItems: 'center'}}><span className='evidence-num'>02</span><div><b>Transaction Stability & Consistency</b><p style={{margin: 0, fontSize: 9.5, color: '#70818d'}}>Stable business rhythm strengthens behavioural evidence.</p></div></div><strong style={{font: '800 16px Manrope', color: '#102333'}}>89%</strong></div>
        <div className='evidence-card'><div style={{display: 'flex', alignItems: 'center'}}><span className='evidence-num'>03</span><div><b>Merchant Customer Score</b><p style={{margin: 0, fontSize: 9.5, color: '#70818d'}}>Customer diversity and healthy recurrence provide stronger evidence.</p></div></div><strong style={{font: '800 16px Manrope', color: '#102333'}}>83%</strong></div>
        <div className='evidence-card'><div style={{display: 'flex', alignItems: 'center'}}><span className='evidence-num'>04</span><div><b>Seasonal Resilience</b><p style={{margin: 0, fontSize: 9.5, color: '#70818d'}}>Performance is evaluated relative to expected seasonal behaviour.</p></div></div><strong style={{font: '800 16px Manrope', color: '#102333'}}>96%</strong></div>
      </div>
    </div>
    <div className='notice-box'>
      <Activity size={16}/>
      <div><b>Prototype assessment notice</b><br/>This interface demonstrates the proposed behavioural credit assessment workflow using demonstration data. Final model outputs, thresholds and lender decisions require validation with real transaction data.</div>
    </div>
  </>;
}


function Alert({title, state, text}) {
  return <div className='alert'><div className='alert-icon' style={{background: '#f0f5f7', color: '#3b5162'}}><CircleCheck size={15}/></div><div><b>{title}</b><p>{text}</p></div><span className='badge good'>{state}</span></div>;
}

createRoot(document.getElementById('root')).render(<App/>);