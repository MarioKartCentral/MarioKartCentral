import { sveltekit } from '@sveltejs/kit/vite'

/** @type {import('vite').UserConfig} */
const config = {
	plugins: [sveltekit()],
	server: { port: 8001 },
	preview: { port: 8001 },
}

export default config;