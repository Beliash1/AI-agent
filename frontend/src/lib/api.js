export async function askAgent(prompt, model = "qwen2.5:7b") {
    const res = await fetch("/agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, model })
    });

    if (!res.ok) {
        throw new Error("Backend connection failed");
    }

    return await res.json();
}
