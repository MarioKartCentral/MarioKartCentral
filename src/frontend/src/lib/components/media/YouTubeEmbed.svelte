<!-- YouTube Video Embed Component -->
<script lang="ts">
  export let url: string;
  export let width: string = '100%';
  export let height: string = '315';
  export let allowFullscreen: boolean = true;
  export let autoplay: boolean = false;
  export let startTime: number | null = null;

  let embedUrl: string = '';
  let isValidYouTube: boolean = false;

  function extractYouTubeVideoId(url: string): string | null {
    // Handle various YouTube URL formats
    const patterns = [
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)/,
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]+)/,
      /(?:https?:\/\/)?youtu\.be\/([a-zA-Z0-9_-]+)/,
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([a-zA-Z0-9_-]+)/,
    ];

    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) {
        return match[1];
      }
    }

    return null;
  }

  function buildEmbedUrl(videoId: string): string {
    const params = new URLSearchParams();

    if (autoplay) params.set('autoplay', '1');
    if (startTime) params.set('start', startTime.toString());
    params.set('rel', '0'); // Don't show related videos
    params.set('modestbranding', '1'); // Minimal YouTube branding

    const paramString = params.toString();
    return `https://www.youtube.com/embed/${videoId}${paramString ? '?' + paramString : ''}`;
  }

  $: {
    const videoId = extractYouTubeVideoId(url);
    if (videoId) {
      isValidYouTube = true;
      embedUrl = buildEmbedUrl(videoId);
    } else {
      isValidYouTube = false;
      embedUrl = '';
    }
  }
</script>

{#if isValidYouTube}
  <div class="youtube-embed-container" style="width: {width};">
    <iframe
      src={embedUrl}
      {width}
      {height}
      frameborder="0"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowfullscreen={allowFullscreen}
      loading="lazy"
      title="YouTube video"
      class="rounded-lg shadow-md"
    ></iframe>

    <!-- Original URL link -->
    <p class="text-xs text-center mt-2 text-gray-500">
      <a href={url} target="_blank" rel="noopener noreferrer" class="hover:text-blue-500 break-all">
        {url}
      </a>
    </p>
  </div>
{:else}
  <!-- Fallback for invalid YouTube URLs -->
  <div class="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
    <p class="text-red-700 text-sm mb-2">Invalid YouTube URL</p>
    <a href={url} target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 text-sm break-all">
      {url}
    </a>
  </div>
{/if}

<style>
  .youtube-embed-container {
    position: relative;
  }

  iframe {
    display: block;
    margin: 0 auto;
  }

  /* Responsive iframe */
  @media (max-width: 640px) {
    iframe {
      width: 100%;
      height: 200px;
    }
  }
</style>
