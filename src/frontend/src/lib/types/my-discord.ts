export type MyDiscord = {
    user_id: number;
    discord_id: string;
    username: string;
    discriminator: string;
    global_name: string | null;
    avatar: string | null;
    token_expires_on: number;
}