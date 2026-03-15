/**
 * app.js - Bot Detector frontend logic
 *
 * Handles form submission, API calls, preset loading,
 * result rendering, input validation, and analysis history.
 */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('analyze-form');
    const analyzeBtn = document.getElementById('analyze-btn');
    const emptyState = document.getElementById('empty-state');
    const resultsContent = document.getElementById('results-content');
    const advancedFields = document.getElementById('advanced-fields');
    const errorBanner = document.getElementById('error-banner');
    const errorMessage = document.getElementById('error-message');
    const errorClose = document.getElementById('error-close');

    // ---- History ----
    const analysisHistory = [];
    const MAX_HISTORY = 3;

    // ---- Error Banner ----
    function showError(msg) {
        errorMessage.textContent = msg;
        errorBanner.classList.remove('hidden');
    }

    function hideError() {
        errorBanner.classList.add('hidden');
    }

    errorClose.addEventListener('click', hideError);

    // ---- Mode Toggle ----
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            advancedFields.classList.toggle('hidden', btn.dataset.mode !== 'advanced');
        });
    });

    // ---- Presets ----
    const presets = {
        human: {
            username: 'sarah_designs',
            account_age_days: 2190,
            total_tweets: 3200,
            followers_count: 850,
            following_count: 420,
            favorites_count: 8500,
            retweet_ratio: 0.2,
            has_profile_image: true,
            has_bio: true,
            is_verified: false,
            bio_length: 120,
            listed_count: 12,
            avg_tweets_per_hour_variance: 8.5,
            unique_sources_count: 3,
            has_url: true,
            has_default_profile: false,
        },
        spam: {
            username: 'xbot384729_promo',
            account_age_days: 12,
            total_tweets: 15000,
            followers_count: 8,
            following_count: 4500,
            favorites_count: 20,
            retweet_ratio: 0.92,
            has_profile_image: false,
            has_bio: false,
            is_verified: false,
            bio_length: 0,
            listed_count: 0,
            avg_tweets_per_hour_variance: 0.3,
            unique_sources_count: 1,
            has_url: true,
            has_default_profile: true,
        },
        farm: {
            username: 'user2847291047',
            account_age_days: 90,
            total_tweets: 45,
            followers_count: 3,
            following_count: 6800,
            favorites_count: 10,
            retweet_ratio: 0.1,
            has_profile_image: false,
            has_bio: false,
            is_verified: false,
            bio_length: 0,
            listed_count: 0,
            avg_tweets_per_hour_variance: 1.2,
            unique_sources_count: 1,
            has_url: false,
            has_default_profile: true,
        },
        content_bot: {
            username: 'NewsBot_AutoFeed',
            account_age_days: 300,
            total_tweets: 48000,
            followers_count: 2400,
            following_count: 190,
            favorites_count: 320,
            retweet_ratio: 0.88,
            has_profile_image: true,
            has_bio: true,
            is_verified: false,
            bio_length: 42,
            listed_count: 9,
            avg_tweets_per_hour_variance: 0.7,
            unique_sources_count: 1,
            has_url: true,
            has_default_profile: false,
        },
    };

    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const preset = presets[btn.dataset.preset];
            if (!preset) return;

            setInput('username', preset.username);
            setInput('account_age_days', preset.account_age_days);
            setInput('total_tweets', preset.total_tweets);
            setInput('followers_count', preset.followers_count);
            setInput('following_count', preset.following_count);
            setInput('favorites_count', preset.favorites_count);
            setInput('retweet_ratio', preset.retweet_ratio);
            setCheckbox('has_profile_image', preset.has_profile_image);
            setCheckbox('has_bio', preset.has_bio);
            setCheckbox('is_verified', preset.is_verified);
            setInput('bio_length', preset.bio_length);
            setInput('listed_count', preset.listed_count);
            setInput('avg_tweets_per_hour_variance', preset.avg_tweets_per_hour_variance);
            setInput('unique_sources_count', preset.unique_sources_count);
            setCheckbox('has_url', preset.has_url);
            setCheckbox('has_default_profile', preset.has_default_profile);

            form.dispatchEvent(new Event('submit'));
        });
    });

    // ---- Input Validation ----
    function validateFormData(data) {
        if (data.account_age_days < 1) return 'Account age must be at least 1 day.';
        if (data.followers_count < 0) return 'Followers cannot be negative.';
        if (data.following_count < 1) return 'Following count must be at least 1.';
        if (data.total_tweets < 0) return 'Total tweets cannot be negative.';
        if (data.favorites_count < 0) return 'Favorites cannot be negative.';
        if (data.retweet_ratio < 0 || data.retweet_ratio > 1) return 'Retweet ratio must be between 0 and 1.';
        if (data.bio_length < 0) return 'Bio length cannot be negative.';
        if (data.listed_count < 0) return 'Listed count cannot be negative.';
        if (data.unique_sources_count < 0) return 'Unique sources cannot be negative.';
        return null;
    }

    // ---- Form Submission ----
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideError();

        const data = collectFormData();
        const validationError = validateFormData(data);
        if (validationError) {
            showError(validationError);
            return;
        }

        analyzeBtn.classList.add('loading');
        analyzeBtn.textContent = '';

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (result.error) {
                showError('Analysis failed: ' + result.error);
                return;
            }

            renderResults(result);
            addToHistory(result, data);

        } catch (err) {
            showError('Could not reach server. Make sure the app is running.');
        } finally {
            analyzeBtn.classList.remove('loading');
            analyzeBtn.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
                </svg>
                Analyze Account
            `;
        }
    });

    // ---- Collect Form Data ----
    function collectFormData() {
        const get = (name) => {
            const el = form.querySelector(`[name="${name}"]`);
            if (!el) return undefined;
            if (el.type === 'checkbox') return el.checked ? 1 : 0;
            return el.value;
        };

        return {
            username: get('username') || '',
            account_age_days: parseInt(get('account_age_days')) || 365,
            total_tweets: parseInt(get('total_tweets')) || 0,
            followers_count: parseInt(get('followers_count')) || 0,
            following_count: parseInt(get('following_count')) || 1,
            favorites_count: parseInt(get('favorites_count')) || 0,
            retweet_ratio: parseFloat(get('retweet_ratio')) || 0.3,
            has_profile_image: get('has_profile_image'),
            has_bio: get('has_bio'),
            is_verified: get('is_verified'),
            bio_length: parseInt(get('bio_length')) || 80,
            listed_count: parseInt(get('listed_count')) || 0,
            avg_tweets_per_hour_variance: parseFloat(get('avg_tweets_per_hour_variance')) || 5.0,
            unique_sources_count: parseInt(get('unique_sources_count')) || 2,
            has_url: get('has_url'),
            has_default_profile: get('has_default_profile'),
        };
    }

    // ---- Render Results ----
    function renderResults(result) {
        emptyState.classList.add('hidden');
        resultsContent.classList.remove('hidden');

        const isBot = result.is_bot;

        // Verdict
        const verdictCard = document.getElementById('verdict-card');
        verdictCard.className = `verdict-card ${isBot ? 'bot' : 'human'}`;
        document.getElementById('verdict-icon').textContent = isBot ? '🤖' : '👤';
        document.getElementById('verdict-label').textContent = isBot ? 'Likely Bot' : 'Likely Human';
        document.getElementById('verdict-confidence').textContent =
            `${result.confidence}% confidence · ${result.bot_probability}% bot probability`;

        // Gauge
        const botPct = result.bot_probability;
        const gaugeFill = document.getElementById('gauge-fill');
        const gaugeMarker = document.getElementById('gauge-marker');

        gaugeFill.style.width = '0%';
        gaugeMarker.style.left = '0%';

        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                gaugeFill.style.width = botPct + '%';
                gaugeMarker.style.left = `calc(${botPct}% - 2px)`;

                if (botPct < 30) {
                    gaugeFill.style.background = 'linear-gradient(90deg, var(--green), #34d399)';
                } else if (botPct < 60) {
                    gaugeFill.style.background = 'linear-gradient(90deg, var(--yellow), #fbbf24)';
                } else {
                    gaugeFill.style.background = 'linear-gradient(90deg, var(--yellow), var(--red))';
                }
            });
        });

        document.getElementById('human-pct').textContent = result.human_probability + '%';
        document.getElementById('bot-pct').textContent = result.bot_probability + '%';

        // Red Flags
        const flagsSection = document.getElementById('flags-section');
        const flagsList = document.getElementById('flags-list');
        flagsList.innerHTML = '';
        flagsSection.classList.remove('hidden');

        if (result.flags && result.flags.length > 0) {
            result.flags.forEach((flag, i) => {
                const el = document.createElement('div');
                el.className = 'flag-item';
                el.style.animationDelay = `${i * 0.08}s`;
                el.innerHTML = `
                    <span class="flag-icon">⚠</span>
                    <div>
                        <div class="flag-label">${flag.flag}</div>
                        <div class="flag-value">${flag.label}: ${formatValue(flag.value)}</div>
                    </div>
                `;
                flagsList.appendChild(el);
            });
        } else {
            flagsList.innerHTML = '<div class="no-flags">✓ No red flags detected. Account appears normal.</div>';
        }

        // Feature Breakdown
        const grid = document.getElementById('features-grid');
        grid.innerHTML = '';

        const maxImportance = Math.max(...result.top_features.map(f => f.importance));

        // High-importance bot signal features get a different bar color
        const botSignalFeatures = new Set([
            'avg_tweets_per_hour_variance', 'retweet_ratio', 'username_digit_ratio',
            'tweets_per_day', 'unique_sources_count', 'has_default_profile',
        ]);

        result.top_features.forEach((feat, i) => {
            const barWidth = (feat.importance / maxImportance) * 100;
            const isSignal = botSignalFeatures.has(feat.feature);
            const row = document.createElement('div');
            row.className = 'feature-row';
            row.style.animationDelay = `${i * 0.05}s`;
            row.innerHTML = `
                <span class="feature-name">${feat.label}</span>
                <span class="feature-value">${formatValue(feat.value)}</span>
                <div class="feature-bar-track">
                    <div class="feature-bar-fill${isSignal ? ' bot-signal' : ''}" style="width: 0%"></div>
                </div>
            `;
            grid.appendChild(row);

            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    row.querySelector('.feature-bar-fill').style.width = barWidth + '%';
                });
            });
        });

        if (window.innerWidth <= 900) {
            resultsContent.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    // ---- History ----
    function addToHistory(result, formData) {
        analysisHistory.unshift({
            name: formData.username || 'Unknown',
            isBot: result.is_bot,
            confidence: result.confidence,
            botProbability: result.bot_probability,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        });
        if (analysisHistory.length > MAX_HISTORY) analysisHistory.pop();
        renderHistory();
    }

    function renderHistory() {
        const section = document.getElementById('history-section');
        const list = document.getElementById('history-list');

        section.classList.remove('hidden');
        list.innerHTML = '';

        analysisHistory.forEach((entry, i) => {
            const item = document.createElement('div');
            item.className = `history-item ${entry.isBot ? 'bot' : 'human'}`;
            item.style.animationDelay = `${i * 0.06}s`;
            item.innerHTML = `
                <span class="history-verdict-icon">${entry.isBot ? '🤖' : '👤'}</span>
                <div class="history-info">
                    <div class="history-name">${entry.name}</div>
                    <div class="history-meta">${entry.isBot ? 'Bot' : 'Human'} · ${entry.time}</div>
                </div>
                <span class="history-confidence">${entry.confidence}%</span>
            `;
            list.appendChild(item);
        });
    }

    // ---- Helpers ----
    function formatValue(val) {
        if (typeof val === 'number') {
            if (Number.isInteger(val)) return val.toLocaleString();
            return parseFloat(val.toFixed(4)).toString();
        }
        return val;
    }

    function setInput(name, value) {
        const el = form.querySelector(`[name="${name}"]`);
        if (el && el.type !== 'checkbox') el.value = value;
    }

    function setCheckbox(name, checked) {
        const el = form.querySelector(`[name="${name}"]`);
        if (el && el.type === 'checkbox') el.checked = !!checked;
    }
});
