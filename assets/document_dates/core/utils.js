/*
    工具函数
*/

// 语言存储与获取
const LANGUAGE_STORAGE_KEY = 'document_dates_language';

window.ddUtils = {
    // 处理 timeago 的 locale 格式
    resolveTimeagoLocale(rawLocale) {
        // 兼容 「ISO 639、ISO 3166、BCP 47」 格式
        const shortLang = rawLocale.trim().replace(/-/g, '_').split('_')[0];
        const fixLocale = {
            bn: 'bn_IN',
            en: 'en_US',
            hi: 'hi_IN',
            id: 'id_ID',
            nb: 'nb_NO',
            nn: 'nn_NO',
            pt: 'pt_BR',
            zh: 'zh_CN'
        };
        return fixLocale[shortLang] || shortLang;
    },

    // 保存当前语言到 localStorage
    saveLanguage(langCode) {
        if (langCode) {
            try {
                localStorage.setItem(LANGUAGE_STORAGE_KEY, langCode);
            } catch (e) {
                console.warn('Failed to save language preference:', e);
            }
        }
    },

    // 从 localStorage 获取保存的语言
    getSavedLanguage() {
        try {
            return localStorage.getItem(LANGUAGE_STORAGE_KEY);
        } catch (e) {
            console.warn('Failed to get saved language preference:', e);
            return null;
        }
    },

    // 清除保存的语言设置
    clearLanguage() {
        try {
            localStorage.removeItem(LANGUAGE_STORAGE_KEY);
        } catch (e) {
            console.warn('Failed to clear language preference:', e);
        }
    }
};