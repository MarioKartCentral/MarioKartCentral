<!-- Universal Media Embed Component -->
<script lang="ts">
    import YouTubeEmbed from './YouTubeEmbed.svelte';
    import TwitterEmbed from './TwitterEmbed.svelte';
    
    export let url: string;
    export let fallbackText: string = 'Open Link';
    export let showOriginalLink: boolean = true;
    export let autoDetect: boolean = true;
    export let embedWidth: string = '100%';
    export let embedHeight: string = '315';
    
    type MediaType = 'youtube' | 'twitter' | 'twitch' | 'image' | 'video' | 'unknown';
    
    let mediaType: MediaType = 'unknown';
    
    function detectMediaType(url: string): MediaType {
        const lowerUrl = url.toLowerCase();
        
        // YouTube detection
        if (lowerUrl.includes('youtube.com') || lowerUrl.includes('youtu.be')) {
            return 'youtube';
        }
        
        // Twitter/X detection
        if (lowerUrl.includes('twitter.com') || lowerUrl.includes('x.com') || lowerUrl.includes('t.co')) {
            return 'twitter';
        }
        
        // Twitch detection
        if (lowerUrl.includes('twitch.tv') || lowerUrl.includes('clips.twitch.tv')) {
            return 'twitch';
        }
        
        // Image detection
        if (/\.(jpg|jpeg|png|gif|webp|bmp|svg)(\?|$)/i.test(url)) {
            return 'image';
        }
        
        // Video detection
        if (/\.(mp4|webm|ogg|avi|mov|wmv|flv)(\?|$)/i.test(url)) {
            return 'video';
        }
        
        return 'unknown';
    }
    
    function getTwitchEmbedUrl(url: string): string {
        // Handle Twitch clip URLs
        if (url.includes('clips.twitch.tv')) {
            const clipId = url.split('/').pop()?.split('?')[0];
            return `https://clips.twitch.tv/embed?clip=${clipId}&parent=${window.location.hostname}`;
        }
        
        // Handle regular Twitch video URLs
        const videoMatch = url.match(/twitch\.tv\/videos\/(\d+)/);
        if (videoMatch) {
            return `https://player.twitch.tv/?video=${videoMatch[1]}&parent=${window.location.hostname}`;
        }
        
        return url;
    }
    
    $: if (autoDetect) {
        mediaType = detectMediaType(url);
    }
</script>

<div class="media-embed-container">
    {#if mediaType === 'youtube'}
        <YouTubeEmbed {url} width={embedWidth} height={embedHeight} />
    
    {:else if mediaType === 'twitter'}
        <TwitterEmbed {url} />
    
    {:else if mediaType === 'twitch'}
        <div class="twitch-embed">
            <iframe
                src={getTwitchEmbedUrl(url)}
                width={embedWidth}
                height={embedHeight}
                frameborder="0"
                scrolling="no"
                allowfullscreen
                title="Twitch video"
                class="rounded-lg shadow-md"
            ></iframe>
            {#if showOriginalLink}
                <p class="text-xs text-center mt-2 text-gray-500">
                    <a href={url} target="_blank" rel="noopener noreferrer" class="hover:text-purple-500 break-all">
                        {url}
                    </a>
                </p>
            {/if}
        </div>
    
    {:else if mediaType === 'image'}
        <div class="image-embed">
            <img 
                src={url} 
                alt="Proof evidence" 
                class="w-full max-h-96 object-contain rounded-lg border border-gray-300 shadow-md"
                loading="lazy"
                on:error={() => mediaType = 'unknown'}
            />
            {#if showOriginalLink}
                <p class="text-sm text-center mt-2">
                    <a href={url} target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800">
                        View full size
                    </a>
                </p>
            {/if}
        </div>
    
    {:else if mediaType === 'video'}
        <div class="video-embed">
            <video 
                controls 
                class="w-full max-h-96 rounded-lg border border-gray-300 shadow-md"
                preload="metadata"
                title="Proof video"
            >
                <source src={url} />
                <track kind="captions" src="" label="No captions available" default />
                Your browser does not support the video tag.
            </video>
            {#if showOriginalLink}
                <p class="text-xs text-center mt-2 text-gray-500">
                    <a href={url} target="_blank" rel="noopener noreferrer" class="hover:text-blue-500 break-all">
                        {url}
                    </a>
                </p>
            {/if}
        </div>
    
    {:else}
        <!-- Unknown/unsupported media type -->
        <div class="fallback-embed bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
            <div class="mb-4">
                <svg class="w-12 h-12 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
            </div>
            <a 
                href={url} 
                target="_blank" 
                rel="noopener noreferrer" 
                class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                {fallbackText}
            </a>
            {#if showOriginalLink}
                <p class="text-xs mt-3 text-gray-500 break-all">{url}</p>
            {/if}
        </div>
    {/if}
</div>

<style>
    .media-embed-container {
        max-width: 100%;
        margin: 0 auto;
    }
    
    .twitch-embed iframe {
        display: block;
        margin: 0 auto;
    }
    
    .image-embed img {
        display: block;
        margin: 0 auto;
    }
    
    .video-embed video {
        display: block;
        margin: 0 auto;
    }
    
    @media (max-width: 640px) {
        .twitch-embed iframe {
            height: 200px;
        }
    }
</style>
