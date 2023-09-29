<script lang="ts">
    import { fade } from 'svelte/transition';

    let dialog: HTMLDialogElement;
    export let header: string | null = null;

    export function open() {
        dialog.showModal();
    }

    export function close() {
        dialog.close();
    }

</script>

<dialog bind:this={dialog} transition:fade={{duration: 3000}}>
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <div class="outer" on:click={close}>
        <div class="container" on:click|stopPropagation>
            <div class="header">
                <div>
                    {#if header}
                        <h3>{header}</h3>
                    {/if}
                </div>
                <div class="exit">
                    <button on:click={close}>X</button>
                </div>
            </div>
            <div class="content">
                <slot/>
            </div>
        </div>
    </div>
</dialog>

<style>
    dialog {
        position: fixed;
        width: 100%;
        height: 100%;
        background-color: transparent;
        color: white;
        border: none;
        outline: 0;
        animation: fade-in 500ms;
    }
    dialog::backdrop {
        background: rgba(0, 0, 0, 0.5);
        animation: fade-in 500ms;
    }
    .outer {
        width: 100%;
        height: 100%;
    }
    .container {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 400px;
        height: 200px;
        margin-left: -200px;
        margin-top: -100px;
        background-color: rgba(255, 255, 255, 0.15);
    }
    .header {
        display: grid;
        background-color: rgba(0, 128, 0, 0.6);
        padding: 15px;
        min-height: 50px;
    }
    .content {
        padding: 15px;
    }
    .exit {
        position: absolute;
        right: 5%;
    }
    button {
        background-color: transparent;
        outline: none;
        border: none;
        cursor: pointer;
    }
    @keyframes fade-in {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
</style>