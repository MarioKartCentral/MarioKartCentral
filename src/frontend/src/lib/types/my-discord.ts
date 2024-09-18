import type { Discord } from "./discord";

export type MyDiscord = Discord & {
    user_id: number;
}