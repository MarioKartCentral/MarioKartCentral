<script lang="ts">
    import Button from "./buttons/Button.svelte";
    import CancelButton from "./buttons/CancelButton.svelte";
    import LL from "$i18n/i18n-svelte";

    export let file: string | null; //base 64 representation of the file
    export let name: string;

    let file_info: File | null;
    let file_list: FileList | null;
    let input: HTMLInputElement;

    function to_base_64 (f: File) {
        const reader = new FileReader();
        reader.readAsDataURL(f);
        reader.onloadend = () => {
            let result = reader.result as string | null;
            file = result ? result.split(',')[1] : result;
            console.log(file);
        }
    }

    function verify_file(fl: FileList | null) {
        if(fl && fl.length) {
            file_info = fl[0];
            if(file_info.size > 1024*1024) {
                alert("Image must be below 1MB");
                file_info = null;
                file_list = null;
                file = null;
                return;
            }
            to_base_64(file_info);
        }
        else {
            file_info = null;
            file = null;
        }
    }

    $: verify_file(file_list);

    function onClick(event: MouseEvent) {
        event.preventDefault();
        input.click();
    }
</script>

{#if !file_info}
    <input accept="image/png, image/jpeg" bind:files={file_list} name={name} type="file" bind:this={input}/>
    <Button type="button" on:click={onClick}>{$LL.COMMON.UPLOAD_IMAGE()}</Button>
{:else}
    <div class="file-info">
        <CancelButton on:click={() => file_list = null}/>
        <div>
            {file_info.name}
        </div>
    </div>
    <img src={URL.createObjectURL(file_info)} alt="file"/>
{/if}

<style>
    img {
        max-width: 100px;
        max-height: 100px;
    }
    input[type="file"] {
        display: none;
    }
    .file-info {
        display: flex;
        align-items: center;
        gap: 5px;
        margin-bottom: 10px;
    }
</style>