import os
import time

model = None
tokenizer = None

def load_model_and_tokenizer(model_path):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    model = AutoModelForCausalLM.from_pretrained(model_path, device_map="cuda:0", torch_dtype=torch.float16, trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    return model, tokenizer

def save_proposal(part_number, content):
    with open("proposals.md", "a") as f:
        f.write(f"\n\n## Part {part_number}\n")
        f.write(content)

# Low temperature to avoid randomness
def run_inference(input_text, temperature=0.2):
    from transformers import pipeline
    try:
        global model, tokenizer
        if model is None or tokenizer is None:
            model_path = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
            model, tokenizer = load_model_and_tokenizer(model_path)

        messages = [
            {"role":"system","content":"""You are a code analysis helper for the RTS Dawn of Machines.
             Provide code change proposals to increase code efficiency. Proposal should have the following format: Previous code, proposed code, brief description of why.
             Provide as many proposals as you can. Be brief in each."""},
            {"role":"system","content":"""
            CODEBASE CONTEXT - Dawn of Machines RTS backend (server.js, Node.js + Socket.io)

            GAME LOOP: runs every 50ms via setInterval. Order: drainElectricity → generateElectricity → computePlayersSight → resolveActions. Every millisecond saved here matters.

            CORE STATE:
            - games: all active games in memory, never persisted
            - game.players: keyed by socket.id. Each player has resources (iron, steel, carbon, graphene, electricity), a sight Set of visible tileIds, a discovered Set of all ever-seen tileIds, and a hackIds Set of acquired hack tokens
            - game.units: keyed by unitId. Each unit has x/z coordinates, a position (tileId = z*32+x), a sight Set, integrity, speed, and a player (socket.id)
            - game.buildings: same structure as units but immobile
            - game.board: 1024 tiles (32x32), each tile holds references to unit/building/resource by id
            - game.actions: flat array of all in-flight actions. Iterated every 50ms. This is the hottest loop in the codebase.
            - game.unitsByPlayer, game.buildingsByPlayer, game.buildingsByType: index Maps to avoid full scans

            ELECTRICITY: drains 0.1 per tick per player + 0.2 per active action belonging to that player. Generators add 0.4 per tick each. Electricity at 0 = game over for that player.

            SIGHT: computed every tick by merging all unit and building sight Sets per player. Expensive when many units are moving.

            SINGLE FILE: server.js only. No modules.

            Apply modern JavaScript (ES2022+), Node.js, and Socket.io best practices.
            There MUST be a performance gain in EACH proposal. 
            There MUST be a change in each proposal. Previous code CANNOT be the same as proposed code.
            Do NOT offer proposals that only offer a small performance increase. Aim for as much performance increase as possible.
            Do NOT provide improvements on readability and cleanliness now. Focus SOLELY on efficiency and performance.
            """},
            {"role":"user", "content": input_text},
        ]

        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
        )

        generation_args = {
            "max_new_tokens": 2000,
            "return_full_text": False,
            "temperature": temperature,
            "do_sample": temperature > 0,
        }

        output = pipe(messages, **generation_args)
        return output[0]['generated_text']

    except Exception as e:
        import traceback
        return traceback.format_exc()

if __name__ == "__main__":
    file = open("../dawn-of-machines/backend/server.js")
    lines = file.readlines()
    file.close()
    
    mid = len(lines) // 2
    part1 = "".join(lines[:mid])
    part2 = "".join(lines[mid:])
    
    run = 0
    while True:
        run += 1
        print(f"--- RUN {run} PART 1 ---")
        result1 = run_inference(part1)
        print("Output 1:", result1)
        save_proposal(f"{run}-1", result1)

        print(f"--- RUN {run} PART 2 ---")
        result2 = run_inference(part2)
        print("Output 2:", result2)
        save_proposal(f"{run}-2", result2)

        time.sleep(2)