<!-- Twitter/X Tweet Embed Component -->
<script lang="ts">
    import { onMount } from 'svelte';
    
    export let url: string;
    export let theme: 'light' | 'dark' = 'light';
    
    let tweetContainer: HTMLDivElement;
    let isValidTweet: boolean = false;
    let isLoading: boolean = true;
    let currentUrl: string = '';
    
    function extractTweetId(url: string): string | null {
        const patterns = [
            /(?:https?:\/\/)?(?:www\.)?twitter\.com\/\w+\/status\/(\d+)/,
            /(?:https?:\/\/)?(?:www\.)?x\.com\/\w+\/status\/(\d+)/,
        ];
        
        for (const pattern of patterns) {
            const match = url.match(pattern);
            if (match && match[1]) {
                return match[1];
            }
        }
        return null;
    }
    
    function extractUsername(url: string): string | null {
        const patterns = [
            /(?:https?:\/\/)?(?:www\.)?twitter\.com\/(\w+)\/status\/\d+/,
            /(?:https?:\/\/)?(?:www\.)?x\.com\/(\w+)\/status\/\d+/,
        ];
        
        for (const pattern of patterns) {
            const match = url.match(pattern);
            if (match && match[1]) {
                return match[1];
            }
        }
        return null;
    }
    
    async function loadTwitterScript(): Promise<void> {
        return new Promise((resolve, reject) => {
            if ((window as any).twttr) {
                resolve();
                return;
            }
            
            const script = document.createElement('script');
            script.src = 'https://platform.twitter.com/widgets.js';
            script.async = true;
            script.charset = 'utf-8';
            
            const timeout = setTimeout(() => {
                reject(new Error('Twitter script loading timeout'));
            }, 15000);
            
            script.onload = () => {
                clearTimeout(timeout);
                const checkTwttr = () => {
                    if ((window as any).twttr?.widgets) {
                        resolve();
                    } else {
                        setTimeout(checkTwttr, 300);
                    }
                };
                checkTwttr();
            };
            
            script.onerror = () => {
                clearTimeout(timeout);
                reject(new Error('Failed to load Twitter widgets'));
            };
            
            document.head.appendChild(script);
        });
    }
    
    function createCustomTweetCard(tweetId: string, username: string) {
        const card = document.createElement('div');
        card.className = 'custom-tweet-card';
        card.innerHTML = `
            <div class="tweet-card-header">
                <div class="tweet-avatar">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                    </svg>
                </div>
                <div class="tweet-info">
                    <span class="tweet-username">@${username}</span>
                    <span class="tweet-separator">•</span>
                    <a href="${url}" target="_blank" rel="noopener noreferrer" class="tweet-link">
                        View on X
                    </a>
                </div>
            </div>
            <div class="tweet-content">
                <p>This tweet couldn't be loaded automatically.</p>
            </div>
            <div class="tweet-footer">
                <a href="${url}" target="_blank" rel="noopener noreferrer" class="view-tweet-btn">
                    View Tweet on X →
                </a>
            </div>
        `;
        return card;
    }
    
    function checkTweetRendered(container: HTMLElement): boolean {
        const iframe = container.querySelector('iframe');
        const tweetElement = container.querySelector('.twitter-tweet');
        return !!(iframe || (tweetElement && tweetElement.children.length > 1));
    }
    
    async function loadTweetEmbed() {
        if (!isValidTweet || !tweetContainer) return;
        
        try {
            isLoading = true;
            const tweetId = extractTweetId(url);
            const username = extractUsername(url);
            
            if (!tweetId) throw new Error('Could not extract tweet ID');
            
            tweetContainer.innerHTML = '';
            
            try {
                await loadTwitterScript();
                
                if ((window as any).twttr?.widgets) {
                    const tweetElement = await Promise.race([
                        (window as any).twttr.widgets.createTweet(tweetId, tweetContainer, {
                            theme: theme,
                            dnt: true,
                            conversation: 'none',
                            cards: 'visible'
                        }),
                        new Promise((_, reject) => {
                            setTimeout(() => reject(new Error('createTweet timeout')), 10000);
                        })
                    ]);
                    
                    if (tweetElement) {
                        if (checkTweetRendered(tweetContainer)) {
                            isLoading = false;
                        } else {
                            setTimeout(() => {
                                isLoading = false;
                            }, 500);
                        }
                        return;
                    }
                }
                
                throw new Error('Twitter widgets API not available');
            } catch (widgetError) {
                tweetContainer.innerHTML = '';
                const customCard = createCustomTweetCard(tweetId, username || 'unknown');
                tweetContainer.appendChild(customCard);
                isLoading = false;
            }
        } catch (error) {
            const tweetId = extractTweetId(url);
            const username = extractUsername(url);
            
            if (tweetId && username) {
                tweetContainer.innerHTML = '';
                const customCard = createCustomTweetCard(tweetId, username);
                tweetContainer.appendChild(customCard);
            }
            
            isLoading = false;
        }
    }
    
    $: {
        const tweetId = extractTweetId(url);
        isValidTweet = Boolean(tweetId);
    }
    
    $: if (url !== currentUrl) {
        currentUrl = url;
        if (isValidTweet) {
            loadTweetEmbed();
        }
    }
    
    onMount(() => {
        if (isValidTweet) {
            loadTweetEmbed();
        }
    });
</script>

{#if isValidTweet}
    <div class="tweet-embed-container">
        {#if isLoading}
            <div class="loading-placeholder">
                <div class="loading-spinner"></div>
                <div class="loading-bars">
                    <div class="bar"></div>
                    <div class="bar"></div>
                    <div class="bar"></div>
                </div>
                <p>Loading tweet...</p>
            </div>
        {/if}
        
        <div bind:this={tweetContainer} class="tweet-container" class:fade-in={!isLoading}>
        </div>
    </div>
{:else}
    <div class="invalid-url">
        <p>Invalid Twitter/X URL</p>
        <a href={url} target="_blank" rel="noopener noreferrer">
            {url} →
        </a>
    </div>
{/if}

<style>
    .tweet-embed-container {
        max-width: 550px;
        margin: 0 auto;
    }
    
    .loading-placeholder {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 32px;
        text-align: center;
        animation: pulse 2s infinite;
    }
    
    .loading-spinner {
        width: 32px;
        height: 32px;
        background: #1da1f2;
        border-radius: 50%;
        margin: 0 auto 16px;
    }
    
    .loading-bars {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-bottom: 16px;
    }
    
    .bar {
        height: 16px;
        background: #dee2e6;
        border-radius: 4px;
    }
    
    .bar:nth-child(1) { width: 120px; }
    .bar:nth-child(2) { width: 80px; }
    .bar:nth-child(3) { width: 100px; }
    
    .loading-placeholder p {
        font-size: 14px;
        color: #6c757d;
        margin: 0;
    }
    
    .tweet-container {
        min-height: 50px;
        opacity: 0;
        transition: opacity 0.3s ease-in;
    }
    
    .tweet-container.fade-in {
        opacity: 1;
    }
    
    .tweet-container :global(.twitter-tweet) {
        margin: 0 auto !important;
    }
    
    .tweet-container :global(.custom-tweet-card) {
        border: 1px solid #e1e8ed;
        border-radius: 12px;
        padding: 16px;
        background: white;
        max-width: 500px;
        margin: 0 auto;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    .tweet-container :global(.tweet-card-header) {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
    }
    
    .tweet-container :global(.tweet-avatar) {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #1da1f2;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        margin-right: 12px;
    }
    
    .tweet-container :global(.tweet-info) {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
    }
    
    .tweet-container :global(.tweet-username) {
        font-weight: bold;
        color: #1da1f2;
    }
    
    .tweet-container :global(.tweet-separator) {
        color: #657786;
    }
    
    .tweet-container :global(.tweet-link) {
        color: #1da1f2;
        text-decoration: none;
    }
    
    .tweet-container :global(.tweet-link:hover) {
        text-decoration: underline;
    }
    
    .tweet-container :global(.tweet-content) {
        margin-bottom: 12px;
        line-height: 1.4;
    }
    
    .tweet-container :global(.tweet-footer) {
        border-top: 1px solid #e1e8ed;
        padding-top: 12px;
    }
    
    .tweet-container :global(.view-tweet-btn) {
        display: inline-block;
        padding: 8px 16px;
        background: #1da1f2;
        color: white;
        text-decoration: none;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 500;
    }
    
    .tweet-container :global(.view-tweet-btn:hover) {
        background: #1991db;
    }
    
    .invalid-url {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    
    .invalid-url p {
        color: #856404;
        font-size: 14px;
        margin: 0 0 8px 0;
    }
    
    .invalid-url a {
        color: #1da1f2;
        text-decoration: none;
        font-size: 14px;
        word-break: break-all;
    }
    
    .invalid-url a:hover {
        text-decoration: underline;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
</style>