/*
    1.生成头像
*/
function isLatin(name) {
    return /^[A-Za-z\s]+$/.test(name.trim());
}
function extractInitials(name) {
    name = name.trim();
    if (!name) return '?';
    if (isLatin(name)) {
        const parts = name.toUpperCase().split(/\s+/).filter(Boolean);
        return parts.length >= 2 ? parts[0][0] + parts[parts.length - 1][0] : parts[0][0];
    } else {
        return name[0];
    }
}
function nameToHSL(name, s = 50, l = 55) {
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
        hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    const hue = hash % 360;
    return `hsl(${hue}, ${s}%, ${l}%)`;
}
function generateAvatar() {
    document.querySelectorAll('.avatar-wrapper').forEach(wrapper => {
        const name = wrapper.dataset.name || '';
        const initials = extractInitials(name);
        const bgColor = nameToHSL(name);

        const textEl = wrapper.querySelector('.avatar-text');
        textEl.textContent = initials;
        textEl.style.backgroundColor = bgColor;

        const imgEl = wrapper.querySelector('img.avatar');
        if (imgEl) {
            const src = (imgEl.getAttribute('src') || '').trim();
            if (!src) {
                imgEl.style.display = 'none';
            }
        }
    });
}



/*
    2.处理内容赋值
*/
// 图标键映射表
const iconKeyMap = {
    doc_created: 'created_time',
    doc_modified: 'modified_time',
    doc_author: 'author',
    doc_authors: 'authors'
};
// 处理文档日期和提示内容
function processDocumentDates() {
    document.querySelectorAll('.document-dates-plugin').forEach(ddpEl => {
        // 获取 locale，优先级：用户主动选择 > 服务端显式配置 > 用户浏览器语言 > 站点HTML语言 > 默认英语
        const rawLocale =
            ddUtils.getSavedLanguage() ||
            ddpEl.getAttribute('locale') ||
            navigator.language ||
            navigator.userLanguage ||
            document.documentElement.lang ||
            'en';

        // 处理 time 元素（使用 timeago 时）
        if (typeof timeago !== 'undefined') {
            const tLocale = ddUtils.resolveTimeagoLocale(rawLocale);
            ddpEl.querySelectorAll('time').forEach(timeEl => {
                timeEl.textContent = timeago.format(timeEl.getAttribute('datetime'), tLocale);
            });
        }

        // 处理 tooltip 内容
        const langData = TooltipLanguage.get(rawLocale);
        ddpEl.querySelectorAll('[data-tippy-content]').forEach(tippyEl => {
            const iconEl = tippyEl.querySelector('[data-icon]');
            const rawIconKey = iconEl ? iconEl.getAttribute('data-icon') : '';
            const iconKey = iconKeyMap[rawIconKey] || 'author';
            if (langData[iconKey]) {
                const content = langData[iconKey] + ': ' + tippyEl.dataset.tippyRaw;
                // 更新 data-tippy-content 属性
                tippyEl.dataset.tippyContent = content;
                // 如果 tippy 实例已存在，直接更新内容
                if (tippyEl._tippy) {
                    tippyEl._tippy.setContent(content);
                }
            }
        });
    });
}

// 供外部使用：更新文档日期和 tippy 内容到指定语言（可持久化）
function updateDocumentDates(locale) {
    ddUtils.saveLanguage(locale);
    processDocumentDates();
}
window.ddPlugin = {
    updateLanguage: updateDocumentDates
};



/*
    3.初始化 tippyManager，创建和管理 tippy 实例
*/
function getCurrentTheme() {
    // 基于 Material's light/dark 配色方案返回对应的 tooltip 主题
    const scheme = (document.body && document.body.getAttribute('data-md-color-scheme')) || 'default';
    return scheme === 'slate' ? tooltip_config.theme.dark : tooltip_config.theme.light;
}

function initTippy() {
    // 创建上下文对象，将其传递给钩子并从函数中返回
    const context = { tooltip_config };

    // 创建 tippy 实例
    const tippyInstances = tippy('[data-tippy-content]', {
        ...tooltip_config,
        theme: getCurrentTheme()
    });
    context.tippyInstances = tippyInstances;

    // 添加观察者，监控 Material's 配色变化，自动切换 tooltip 主题
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'data-md-color-scheme') {
                const newTheme = getCurrentTheme();
                tippyInstances.forEach(instance => {
                    instance.setProps({ theme: newTheme });
                });
            }
        });
    });
    observer.observe(document.body, {
        attributes: true,
        attributeFilter: ['data-md-color-scheme']
    });
    context.observer = observer;

    // 返回包含 tippyInstances 和 observer 的上下文，用于后续清理
    return context;
}

// 通过 IIFE（立即执行的函数表达式）创建 tippyManager
const tippyManager = (() => {
    let tippyInstances = [];
    let observer = null;
    function cleanup() {
        // 销毁之前的 tippy 实例
        if (tippyInstances.length > 0) {
            tippyInstances.forEach(instance => instance.destroy());
            tippyInstances = [];
        }
        // 断开之前的观察者连接
        if (observer) {
            observer.disconnect();
            observer = null;
        }
    }
    return {
        // 每一次调用都生成新的实例（兼容 navigation.instant）
        initialize() {
            // 先清理以前的实例
            cleanup();
            // 初始化新实例
            const context = initTippy();
            if (context && context.tippyInstances) {
                tippyInstances = context.tippyInstances;
            }
            if (context && context.observer) {
                observer = context.observer;
            }
        }
    };
})();



/*
    入口: 兼容 Material 主题的 'navigation.instant' 属性
*/
if (typeof window.document$ !== 'undefined' && !window.document$.isStopped) {
    window.document$.subscribe(() => {
        processDocumentDates();
        generateAvatar();
        // 通过 tippyManager 创建 tippy 实例
        tippyManager.initialize();
    });
} else {
    processDocumentDates();
    generateAvatar();
    document.addEventListener('DOMContentLoaded', tippyManager.initialize);
}
