/*
    Tooltip 配置
*/
const ttDefaultConfig = {
    // 可配置: light material, 或在 user.config.css 中自定义的主题
    theme: {
        light: 'light',
        dark: 'material'
    },
    placement: 'bottom',    // 位置: top bottom left right auto
    offset: [0, 12],        // 位置偏移: [horizontal, vertical]
    allowHTML: true,        // 是否允许 HTML 内容
    interactive: true,      // 是否允许内容交互
    animation: 'scale',     // 动画类型: scale shift-away
    inertia: true,          // 是否允许动画惯性
    // arrow: false,           // 是否允许箭头
    // animateFill: true,      // 背景填充颜色是否应为动画效果
    // delay: [400, null],     // 动画延迟: [show, hide]: show 为 400 毫秒, hide 为 null 表示默认值
};
let tooltip_config = { ...ttDefaultConfig };
function setConfig(newConfig) {
    tooltip_config = {
        ...ttDefaultConfig,
        ...newConfig
    };
}
window.TooltipConfig = { setConfig };



/*
    语言包配置
*/
// 通过 IIFE（立即执行的函数表达式）创建 TooltipLanguage
window.TooltipLanguage = (function () {
    const allLangs = new Map();

    /*
    用户 locale 值      匹配顺序（fallback 列表）
    zh-Hans-CN         zh-Hans-CN → zh-Hans → zh → en
    zh_CN              zh-CN → zh → en
    fr-FR              fr-FR → fr → en
    ko                 ko → en
    */
    // 生成 fallback 列表
    function generateFallbacks(locale, defaultLocale = 'en') {
        const normalized = locale.trim().replace(/_/g, '-');
        const parts = normalized.split('-');
        const fallbacks = [];
        for (let i = parts.length - 1; i >= 2; i--) {
            fallbacks.push(parts.slice(0, i).join('-'));
        }
        fallbacks.push(parts[0]);
        if (!fallbacks.includes(defaultLocale)) {
            fallbacks.push(defaultLocale);
        }
        return fallbacks;
    }
    return {
        register(locale, data) {
            // 合并数据，支持字段合并覆盖
            const existingData = allLangs.get(locale) || {};
            allLangs.set(locale, {
                ...existingData,
                ...data
            });
        },
        get(locale) {
            // 优先原值直接匹配
            if (allLangs.has(locale)) return allLangs.get(locale);
            // 进入降级匹配
            const fallbacks = generateFallbacks(locale);
            for (const fallbackLocale of fallbacks) {
                const data = allLangs.get(fallbackLocale);
                if (data) {
                    return data;
                }
            }
            return {};
        }
    };
})();

// 在 IIFE 内部注册默认语言包
(function() {
    const defaultLanguages = {
        ar: {
            created_time: "تاريخ الإنشاء",
            modified_time: "تاريخ التعديل",
            author: "المؤلف",
            authors: "المؤلفون"
        },
        de: {
            created_time: "Erstellungszeit",
            modified_time: "Änderungszeit",
            author: "Autor",
            authors: "Autoren"
        },
        en: {
            created_time: "Created",
            modified_time: "Last Update",
            author: "Author",
            authors: "Authors"
        },
        es: {
            created_time: "Fecha de creación",
            modified_time: "Fecha de modificación",
            author: "Autor",
            authors: "Autores"
        },
        fr: {
            created_time: "Date de création",
            modified_time: "Date de modification",
            author: "Auteur",
            authors: "Auteurs"
        },
        ja: {
            created_time: "作成日時",
            modified_time: "更新日時",
            author: "著者",
            authors: "著者"
        },
        ko: {
            created_time: "작성일",
            modified_time: "수정일",
            author: "작성자",
            authors: "작성자"
        },
        nl: {
            created_time: "Gecreëerd",
            modified_time: "Laatst geüpdatet",
            author: "Auteur",
            authors: "Auteurs"            
        },
        pt: {
            created_time: "Criado em",
            modified_time: "Última atualização",
            author: "Autor",
            authors: "Autores"
        },
        ru: {
            created_time: "Дата создания",
            modified_time: "Дата изменения",
            author: "Автор",
            authors: "Авторы"
        },
        zh: {
            created_time: "创建时间",
            modified_time: "最后更新",
            author: "作者",
            authors: "作者"
        },
        zh_TW: {
            created_time: "建立時間",
            modified_time: "修改時間",
            author: "作者",
            authors: "作者"
        }
    };

    // 统一注册默认语言
    Object.entries(defaultLanguages).forEach(([locale, data]) => {
        TooltipLanguage.register(locale, data);
    });
})();
