// ==UserScript==
// @name         ChatGPT 元素诊断器 v3 · 通用版(支持任意网站)
// @namespace    https://wan22.local/
// @version      3.0.0
// @description  点击启动式诊断面板(抗 React 水合抹除)。已知 ChatGPT 域名自动激活;其他域名在 Tampermonkey 菜单里手动启动,激活一次自动记住。
// @author       You
// @match        *://*/*
// @grant        GM_setClipboard
// @grant        GM_registerMenuCommand
// @grant        GM_setValue
// @grant        GM_getValue
// @run-at       document-idle
// @noframes
// ==/UserScript==

/*
 * v3 变更(见下方行注释,避免 star-slash 破坏块注释)
 */
// - @match 放宽为通用通配符,支持任意网站
// - 已知 ChatGPT 域名自动激活(chatgpt / openai / aimonkey / geek / rockchat / zhile / nowchat 等)
// - 未知域名只在 Tampermonkey 菜单注册"启动诊断面板",点击才注入
// - 永久启用当前域名:一键添加到本地白名单,下次进来自动激活
// - 保持 v2 的所有特性:延迟注入 / 小按钮 / 自愈 / 面板

(function () {
    'use strict';

    // ============================================================
    // 检测目标配置
    // ============================================================
    const TARGETS = [
        {
            id: 'input', name: '💬 输入框',
            desc: '工具用 JS 塞文本的目标 (INPUT_SELECTOR)',
            selectors: [
                '#prompt-textarea',
                'div#prompt-textarea.ProseMirror',
                'div[contenteditable="true"].ProseMirror',
                'textarea[data-id="root"]',
                'textarea[name="prompt-textarea"]',
                'div.ProseMirror[contenteditable="true"]',
                'div[contenteditable="true"]',
                'textarea[placeholder*="问"]',
                'textarea[placeholder*="Message"]',
                'textarea[placeholder*="message"]',
            ],
        },
        {
            id: 'send', name: '📤 发送按钮',
            desc: '工具 click 这个按钮',
            selectors: [
                'button[data-testid="send-button"]',
                'button[data-testid="fruitjuice-send-button"]',
                'button[aria-label*="发送"]',
                'button[aria-label*="Send"]',
                'button[aria-label*="send"]',
                'button[aria-label*="提交"]',
                'form button[type="submit"]',
            ],
        },
        {
            id: 'stop', name: '⏸ 停止生成按钮',
            desc: '存在 = 正在生成',
            selectors: [
                'button[data-testid="stop-button"]',
                'button[aria-label*="停止"]',
                'button[aria-label*="Stop"]',
            ],
        },
        {
            id: 'attach', name: '📎 附件按钮 (+)',
            desc: '有时需要先点它再出现 file input',
            selectors: [
                'button[data-testid="composer-plus-btn"]',
                'button[data-testid="composer-file-upload-button"]',
                'button[aria-label*="附加"]',
                'button[aria-label*="附件"]',
                'button[aria-label*="Attach"]',
                'button[aria-label*="upload"]',
                'button[aria-label*="Upload"]',
                'button[aria-label*="上传"]',
            ],
        },
        {
            id: 'file_input', name: '📂 文件上传 input[type=file]',
            desc: '⭐ 关键 — send_keys(路径) 的目标',
            selectors: [
                'input[type="file"]',
                'input[accept*="image"]',
                'input[multiple][type="file"]',
            ],
            findAll: true,
        },
        {
            id: 'assistant_all', name: '🤖 Assistant 消息(所有)',
            desc: '工具定位最新回复的基础',
            selectors: [
                'div[data-message-author-role="assistant"]',
                'article[data-testid^="conversation-turn"]',
                'div[data-testid^="conversation-turn-"][class*="group"]',
                'main article',
            ],
            findAll: true,
        },
        {
            id: 'last_msg_custom', name: '🎯 最后一条 Assistant 消息',
            desc: '按工具现有逻辑定位',
            custom: function () {
                const nodes = document.querySelectorAll('div[data-message-author-role="assistant"]');
                return nodes.length ? [nodes[nodes.length - 1]] : [];
            },
        },
        {
            id: 'last_images', name: '🖼 最新回复中的 <img>',
            desc: '⭐ 关键 — get_last_images() 的目标',
            findAll: true,
            custom: function () {
                const nodes = document.querySelectorAll('div[data-message-author-role="assistant"]');
                if (!nodes.length) return [];
                const last = nodes[nodes.length - 1];
                return Array.from(last.querySelectorAll('img'));
            },
        },
        {
            id: 'image_srcs', name: '🔗 最新回复中图片的 src',
            desc: '⭐ 最关键 — 这里是空就下载失败',
            findAll: true, textOnly: true,
            custom: function () {
                const nodes = document.querySelectorAll('div[data-message-author-role="assistant"]');
                if (!nodes.length) return [];
                const last = nodes[nodes.length - 1];
                return Array.from(last.querySelectorAll('img')).map(i => ({
                    tagName: 'IMG',
                    _srcText: i.src || '(空 src!)',
                    _info: `${i.naturalWidth}×${i.naturalHeight}, alt="${i.alt || ''}"`,
                }));
            },
        },
        {
            id: 'all_imgs_in_chat', name: '🧪 对话区所有 img(兜底)',
            desc: '最新回复找不到图时用这个看全貌',
            findAll: true,
            custom: function () {
                const main = document.querySelector('main') || document.body;
                return Array.from(main.querySelectorAll('img'))
                    .filter(i => i.src && !i.src.startsWith('data:image/svg'));
            },
        },
        {
            id: 'download_btns', name: '⬇ 图片下载按钮(备用)',
            desc: '如果 img.src 拿不到,可以 click 下载按钮',
            findAll: true,
            custom: function () {
                const nodes = document.querySelectorAll('div[data-message-author-role="assistant"]');
                if (!nodes.length) return [];
                const last = nodes[nodes.length - 1];
                return Array.from(last.querySelectorAll(
                    'button[aria-label*="下载"],button[aria-label*="Download"],a[download]'
                ));
            },
        },
    ];

    // ============================================================
    // 样式
    // ============================================================
    const CSS = `
    #wan22-launcher, #wan22-launcher * { box-sizing: border-box; }
    #wan22-launcher {
        position: fixed !important;
        bottom: 18px !important; right: 18px !important;
        z-index: 2147483647 !important;
        background: #1a1d23 !important;
        color: #7fd4ff !important;
        border: 2px solid #3a7cc0 !important;
        border-radius: 24px !important;
        padding: 10px 16px !important;
        cursor: pointer !important;
        font-family: 'Microsoft YaHei', sans-serif !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 18px rgba(58,124,192,0.5) !important;
        user-select: none !important;
        transition: transform 0.1s ease !important;
    }
    #wan22-launcher:hover {
        transform: scale(1.05) !important;
        background: #2d5b8f !important;
        color: #fff !important;
    }
    #wan22-launcher.active {
        background: #22c55e !important;
        border-color: #16a34a !important;
        color: #fff !important;
    }

    #wan22-panel, #wan22-panel * { box-sizing: border-box; }
    #wan22-panel {
        position: fixed !important;
        top: 10px !important; right: 10px !important;
        z-index: 2147483647 !important;
        width: 460px; max-height: 85vh; overflow: hidden;
        background: #1a1d23 !important; color: #e0e0e0 !important;
        border: 1px solid #3a3f4a; border-radius: 10px;
        font-family: 'JetBrains Mono', 'Consolas', 'Microsoft YaHei', monospace;
        font-size: 11.5px; line-height: 1.45;
        box-shadow: 0 6px 28px rgba(0,0,0,0.6);
        display: flex; flex-direction: column;
    }
    #wan22-panel.min { width: 140px; max-height: 36px; }
    #wan22-panel.min .w22-body, #wan22-panel.min .w22-footer { display: none; }
    .w22-header {
        background: #22262f; padding: 8px 10px;
        display: flex; align-items: center; gap: 8px;
        cursor: move; user-select: none;
        border-bottom: 1px solid #3a3f4a;
    }
    .w22-title { flex: 1; font-weight: 600; color: #7fd4ff; font-size: 12px; }
    .w22-header button {
        background: #2d323c; color: #e0e0e0; border: 1px solid #3a3f4a;
        border-radius: 4px; padding: 3px 8px; cursor: pointer; font-size: 11px;
        font-family: inherit;
    }
    .w22-header button:hover { background: #3a3f4a; color: #fff; }
    .w22-body { overflow-y: auto; flex: 1; padding: 8px 10px; }
    .w22-footer {
        padding: 8px 10px; background: #22262f;
        border-top: 1px solid #3a3f4a;
        display: flex; gap: 6px;
    }
    .w22-footer button {
        flex: 1; background: #2d5b8f; color: #fff;
        border: none; border-radius: 4px; padding: 6px; cursor: pointer;
        font-family: inherit; font-size: 11.5px; font-weight: 600;
    }
    .w22-footer button:hover { background: #3a7cc0; }
    .w22-footer button.scan { background: #2d8f5b; }
    .w22-footer button.scan:hover { background: #3ac082; }
    .w22-target {
        margin-bottom: 8px; padding: 8px; border-radius: 6px;
        background: #22262f; border: 1px solid #2f343d;
    }
    .w22-target.ok { border-left: 3px solid #4ade80; }
    .w22-target.miss { border-left: 3px solid #ef4444; background: #2a1d1d; }
    .w22-target.multi { border-left: 3px solid #facc15; }
    .w22-t-name { font-weight: 600; color: #fff; font-size: 12px; margin-bottom: 2px; }
    .w22-t-desc { color: #888; font-size: 10.5px; margin-bottom: 4px; }
    .w22-t-sel {
        background: #0d0f13; color: #7fd4ff; padding: 4px 6px;
        border-radius: 3px; word-break: break-all; margin: 3px 0;
        font-size: 11px;
    }
    .w22-t-sel.miss { color: #ef4444; }
    .w22-t-count { color: #facc15; font-weight: 600; }
    .w22-t-snippet {
        background: #0d0f13; color: #a8c9e6; padding: 4px 6px;
        border-radius: 3px; margin: 3px 0; font-size: 10.5px;
        max-height: 60px; overflow: auto; white-space: pre-wrap;
        word-break: break-all;
    }
    .w22-t-actions { display: flex; gap: 4px; margin-top: 4px; flex-wrap: wrap; }
    .w22-t-actions button {
        background: #2d323c; color: #e0e0e0; border: 1px solid #3a3f4a;
        border-radius: 3px; padding: 2px 6px; cursor: pointer;
        font-family: inherit; font-size: 10.5px;
    }
    .w22-t-actions button:hover { background: #3a3f4a; color: #fff; }
    .w22-hl { outline: 3px solid #f97316 !important; outline-offset: 2px; }
    .w22-url {
        background: #0d0f13; color: #7fd4ff; padding: 3px 5px;
        border-radius: 3px; font-size: 10.5px;
        word-break: break-all; margin: 2px 0;
    }
    .w22-url.empty { color: #ef4444; }
    .w22-toast {
        position: fixed; top: 60px; right: 20px; z-index: 2147483647;
        background: #22c55e; color: #fff; padding: 10px 16px;
        border-radius: 6px; box-shadow: 0 2px 10px rgba(0,0,0,0.4);
        font-family: 'Microsoft YaHei', monospace; font-size: 12px;
    }
    `;

    let styleInjected = false;
    function injectStyle() {
        const old = document.getElementById('wan22-style');
        if (old && styleInjected) return;
        if (old) old.remove();
        const style = document.createElement('style');
        style.id = 'wan22-style';
        style.textContent = CSS;
        (document.head || document.documentElement).appendChild(style);
        styleInjected = true;
    }

    // ============================================================
    // 工具函数
    // ============================================================
    function copy(text) {
        if (typeof GM_setClipboard === 'function') {
            GM_setClipboard(text);
        } else {
            navigator.clipboard.writeText(text).catch(() => {
                const ta = document.createElement('textarea');
                ta.value = text; document.body.appendChild(ta);
                ta.select(); document.execCommand('copy'); ta.remove();
            });
        }
    }

    function toast(msg, color) {
        const t = document.createElement('div');
        t.className = 'w22-toast';
        t.style.background = color || '#22c55e';
        t.textContent = msg;
        document.documentElement.appendChild(t);
        setTimeout(() => t.remove(), 2500);
    }

    function highlight(el, clear = true) {
        if (clear) document.querySelectorAll('.w22-hl').forEach(e => e.classList.remove('w22-hl'));
        if (el && el.classList) {
            el.classList.add('w22-hl');
            try { el.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch (e) {}
            setTimeout(() => el.classList && el.classList.remove('w22-hl'), 3000);
        }
    }

    function snippet(el, max = 180) {
        if (!el || !el.outerHTML) return '';
        let s = el.outerHTML.replace(/\s+/g, ' ').trim();
        if (s.length > max) s = s.substring(0, max) + '...';
        return s;
    }

    // ============================================================
    // 检测
    // ============================================================
    function detect(target) {
        const result = {
            id: target.id, name: target.name, desc: target.desc,
            matchedSelector: null, count: 0, elements: [],
            allSelectorsResults: [],
        };

        if (target.custom) {
            const els = target.custom();
            result.count = els.length;
            result.elements = els;
            result.matchedSelector = '(custom function)';
        } else {
            for (const sel of target.selectors) {
                try {
                    const els = document.querySelectorAll(sel);
                    result.allSelectorsResults.push({ sel, count: els.length });
                    if (els.length && !result.matchedSelector) {
                        result.matchedSelector = sel;
                        result.count = els.length;
                        result.elements = target.findAll ? Array.from(els) : [els[0]];
                    }
                } catch (e) {
                    result.allSelectorsResults.push({ sel, error: e.message });
                }
            }
        }
        return result;
    }

    // ============================================================
    // 渲染目标条目
    // ============================================================
    function renderTarget(r, target) {
        const statusCls = r.count === 0 ? 'miss'
            : (r.count > 1 && !target.findAll && r.id !== 'last_msg_custom' ? 'multi' : 'ok');
        const wrap = document.createElement('div');
        wrap.className = 'w22-target ' + statusCls;

        const name = document.createElement('div');
        name.className = 'w22-t-name';
        name.innerHTML = r.name + ' <span class="w22-t-count">[' + r.count + ']</span>';
        wrap.appendChild(name);

        if (r.desc) {
            const d = document.createElement('div');
            d.className = 'w22-t-desc'; d.textContent = r.desc;
            wrap.appendChild(d);
        }

        const sel = document.createElement('div');
        sel.className = 'w22-t-sel' + (r.count ? '' : ' miss');
        sel.textContent = r.matchedSelector || '(无匹配 ❌)';
        wrap.appendChild(sel);

        if (target.textOnly && r.elements.length) {
            r.elements.forEach((item, i) => {
                const u = document.createElement('div');
                u.className = 'w22-url' + (!item._srcText || item._srcText === '(空 src!)' ? ' empty' : '');
                u.textContent = '[' + (i + 1) + '] ' + item._srcText + ' | ' + (item._info || '');
                wrap.appendChild(u);
                const ba = document.createElement('div');
                ba.className = 'w22-t-actions';
                const cb = document.createElement('button');
                cb.textContent = '复制 URL';
                cb.onclick = () => { copy(item._srcText); toast('✅ URL 已复制'); };
                ba.appendChild(cb);
                wrap.appendChild(ba);
            });
        } else if (r.count && r.elements.length) {
            r.elements.slice(0, 2).forEach((el, i) => {
                const sn = document.createElement('div');
                sn.className = 'w22-t-snippet';
                sn.textContent = '[' + i + '] ' + snippet(el, 200);
                wrap.appendChild(sn);
            });
            if (r.elements.length > 2) {
                const more = document.createElement('div');
                more.className = 'w22-t-desc';
                more.textContent = '...还有 ' + (r.elements.length - 2) + ' 个未显示';
                wrap.appendChild(more);
            }

            const actions = document.createElement('div');
            actions.className = 'w22-t-actions';
            const b1 = document.createElement('button');
            b1.textContent = '📋 复制选择器';
            b1.onclick = () => { copy(r.matchedSelector); toast('✅ 选择器已复制'); };
            actions.appendChild(b1);
            const b2 = document.createElement('button');
            b2.textContent = '🎯 高亮第一个';
            b2.onclick = () => { highlight(r.elements[0]); toast('🎯 已高亮并滚动'); };
            actions.appendChild(b2);
            if (r.elements[0] && r.elements[0].outerHTML) {
                const b3 = document.createElement('button');
                b3.textContent = '📄 复制 HTML';
                b3.onclick = () => { copy(r.elements[0].outerHTML); toast('✅ HTML 已复制'); };
                actions.appendChild(b3);
            }
            wrap.appendChild(actions);
        }

        if (!target.custom && r.allSelectorsResults.length && r.count === 0) {
            const dbg = document.createElement('details');
            dbg.style.marginTop = '4px';
            const sum = document.createElement('summary');
            sum.textContent = '🔎 所有尝试过的选择器 (' + r.allSelectorsResults.length + ')';
            sum.style.cssText = 'font-size: 10.5px; color: #888; cursor: pointer;';
            dbg.appendChild(sum);
            r.allSelectorsResults.forEach(ar => {
                const line = document.createElement('div');
                line.className = 'w22-t-sel miss';
                line.textContent = ar.sel + '  →  ' + (ar.error ? '💥 ' + ar.error : '[' + ar.count + ']');
                dbg.appendChild(line);
            });
            wrap.appendChild(dbg);
        }

        return wrap;
    }

    // ============================================================
    // 面板(点击按钮后才创建)
    // ============================================================
    let allResults = [];

    function createPanel() {
        const old = document.getElementById('wan22-panel');
        if (old) old.remove();

        const panel = document.createElement('div');
        panel.id = 'wan22-panel';
        panel.innerHTML =
            '<div class="w22-header">' +
            '  <span class="w22-title">🔍 ChatGPT 诊断面板</span>' +
            '  <button class="w22-min-btn">—</button>' +
            '  <button class="w22-close-btn">×</button>' +
            '</div>' +
            '<div class="w22-body"></div>' +
            '<div class="w22-footer">' +
            '  <button class="scan w22-scan-btn">🔄 重新扫描</button>' +
            '  <button class="w22-export-btn">📋 导出完整报告</button>' +
            '</div>';
        document.documentElement.appendChild(panel);

        const body = panel.querySelector('.w22-body');

        function scan() {
            body.innerHTML = '';
            allResults = [];
            const summary = document.createElement('div');
            summary.style.cssText = 'padding: 6px 8px; margin-bottom: 6px; background: #0d0f13; border-radius: 4px; color: #888;';
            summary.textContent = '⏱ ' + new Date().toLocaleString() + '  |  URL: ' + location.hostname;
            body.appendChild(summary);

            TARGETS.forEach(target => {
                const r = detect(target);
                allResults.push(r);
                body.appendChild(renderTarget(r, target));
            });

            const ok = allResults.filter(r => r.count > 0).length;
            summary.textContent += '  |  ' + ok + '/' + TARGETS.length + ' 命中';
        }

        function exportReport() {
            const report = {
                url: location.href,
                userAgent: navigator.userAgent,
                time: new Date().toISOString(),
                viewport: innerWidth + '×' + innerHeight,
                scriptVersion: '3.0.0',
                targets: allResults.map(r => ({
                    id: r.id, name: r.name, desc: r.desc,
                    matchedSelector: r.matchedSelector,
                    count: r.count,
                    allSelectorsResults: r.allSelectorsResults,
                    sampleHTML: r.elements && r.elements[0] ? snippet(r.elements[0], 600) : null,
                    sampleText: r.elements && r.elements[0] && r.elements[0]._srcText ? r.elements[0]._srcText : null,
                })),
            };
            copy(JSON.stringify(report, null, 2));
            toast('📋 完整诊断报告已复制,粘贴给 Claude 即可', '#2563eb');
        }

        panel.querySelector('.w22-scan-btn').onclick = scan;
        panel.querySelector('.w22-export-btn').onclick = exportReport;
        panel.querySelector('.w22-min-btn').onclick = () => {
            panel.classList.toggle('min');
            panel.querySelector('.w22-min-btn').textContent = panel.classList.contains('min') ? '□' : '—';
        };
        panel.querySelector('.w22-close-btn').onclick = () => {
            panel.remove();
            const launcher = document.getElementById('wan22-launcher');
            if (launcher) launcher.classList.remove('active');
        };

        // 拖拽
        const header = panel.querySelector('.w22-header');
        let drag = null;
        header.onmousedown = e => {
            if (e.target.tagName === 'BUTTON') return;
            const rect = panel.getBoundingClientRect();
            drag = { dx: e.clientX - rect.left, dy: e.clientY - rect.top };
            document.onmousemove = e2 => {
                if (!drag) return;
                panel.style.left = (e2.clientX - drag.dx) + 'px';
                panel.style.top = (e2.clientY - drag.dy) + 'px';
                panel.style.right = 'auto';
            };
            document.onmouseup = () => { drag = null; document.onmousemove = null; };
        };

        scan();
        return panel;
    }

    // ============================================================
    // 启动器按钮(常驻 + 自愈)
    // ============================================================
    function ensureLauncher() {
        injectStyle();
        if (document.getElementById('wan22-launcher')) return;

        const btn = document.createElement('div');
        btn.id = 'wan22-launcher';
        btn.innerHTML = '🔍 诊断';
        btn.title = '点击打开/关闭 诊断面板';
        btn.onclick = function (e) {
            e.stopPropagation();
            const existing = document.getElementById('wan22-panel');
            if (existing) {
                existing.remove();
                btn.classList.remove('active');
            } else {
                createPanel();
                btn.classList.add('active');
            }
        };

        // 挂在 documentElement(html 标签下),不挂 body
        document.documentElement.appendChild(btn);
    }

    // ============================================================
    // 激活逻辑:已知域名自动激活 / 未知域名走菜单命令
    // ============================================================

    // 已知 ChatGPT 相关域名关键字(hostname 命中任何一个就自动激活)
    const KNOWN_KEYWORDS = [
        'chatgpt',      // chatgpt.com, chatgpt.nowchat.top, etc.
        'openai',       // openai.com, openai-hk.com, etc.
        'aimonkey',     // gpt.aimonkey.plus
        'geek',         // geekchat / geekai / geekerchat
        'rockchat',     // rockchat.top
        'zhile',        // chat.zhile.io
        'chatplus',
        'chat.' ,       // 一般以 chat.xxx 开头的聊天镜像站
        'gpt.',         // gpt.xxx 镜像
    ];

    const hostname = location.hostname.toLowerCase();

    function isKnownChatSite() {
        return KNOWN_KEYWORDS.some(k => hostname.includes(k));
    }

    // 持久化:记住用户手动启用过的域名
    function isUserEnabled() {
        try {
            return typeof GM_getValue === 'function'
                && GM_getValue('enabled_' + hostname, false) === true;
        } catch (e) { return false; }
    }

    function setUserEnabled(val) {
        try {
            if (typeof GM_setValue === 'function') {
                GM_setValue('enabled_' + hostname, val);
            }
        } catch (e) {}
    }

    let activated = false;

    function activate() {
        if (activated) return;
        activated = true;
        console.log('[Wan22 诊断器 v3] 激活中,3 秒后注入...');
        setTimeout(() => {
            ensureLauncher();
            console.log('[Wan22 诊断器 v3] 启动器已注入(' + hostname + '),开启自愈');
            setInterval(() => {
                try { ensureLauncher(); }
                catch (e) { console.warn('[Wan22] 自愈失败', e); }
            }, 2000);
        }, 3000);
    }

    // 注册菜单命令(无论是什么域名都注册,方便用户临时启动)
    try {
        if (typeof GM_registerMenuCommand === 'function') {
            GM_registerMenuCommand('🔍 启动诊断面板(本次)', () => activate());
            if (isUserEnabled()) {
                GM_registerMenuCommand('🔕 取消永久启用 ' + hostname, () => {
                    setUserEnabled(false);
                    alert('已取消永久启用。刷新后本域名不再自动激活。');
                });
            } else {
                GM_registerMenuCommand('📌 永久启用 ' + hostname, () => {
                    setUserEnabled(true);
                    activate();
                    alert('已永久启用 ' + hostname + '。以后进这个域名会自动激活。');
                });
            }
        }
    } catch (e) {
        console.warn('[Wan22] 菜单注册失败(Tampermonkey 可能版本太旧)', e);
    }

    // 自动激活:已知 ChatGPT 域名 OR 用户永久启用过的域名
    if (isKnownChatSite() || isUserEnabled()) {
        activate();
    } else {
        console.log('[Wan22 诊断器 v3] 当前域名未识别为聊天站。如需使用:'
            + '点 Tampermonkey 图标 → 选"🔍 启动诊断面板(本次)"。');
    }
})();
