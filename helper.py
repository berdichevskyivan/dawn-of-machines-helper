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

            DATA STRUCTURES:
            - games: Map<gameId, game> — game state
            - game.players: Map<socketId, player> — player state: { resources: {iron,steel,carbon,graphene,electricity}, sight: Set, discovered: Set, hackIds: Set }
            - game.units: Map<unitId, unit> — { id, hackId, player(socketId), x, z, position, sight: Set, mobile, integrity, speed }
            - game.buildings: Map<buildingId, building> — { id, hackId, player(socketId), x, z, position, sight: Set, type }
            - game.board: Map<tileId, tile> — 32x32=1024 tiles: { id, x, z, resource, unit, building }
            - game.actions: Array — active action queue, processed every 50ms
            - game.unitsByPlayer: Map<socketId, Set<unitId>>
            - game.buildingsByPlayer: Map<socketId, Set<buildingId>>
            - game.buildingsByType: Map<type, Set<buildingId>>

            GAME LOOP: setInterval 50ms — drainElectricity → generateElectricity → computePlayersSight → resolveActions

            ACTION TYPES: movement, gather, scan, hack, attack, assemble-*, build-*, refine-iron, refine-carbon, electricity-threshold-*

            RESOURCES: iron, carbon, steel, graphene, electricity. Electricity drains 0.1/tick + 0.2 per active action. Generators produce 0.4/tick each.

            SINGLE FILE: server.js. No game.js. No separate modules.

            Apply modern JavaScript (ES2022+), Node.js, and Socket.io best practices.
            There MUST be a performance gain in EACH proposal. 
            There MUST be a change in each proposal. Previous code CANNOT be the same as proposed code.
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