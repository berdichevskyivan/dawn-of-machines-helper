

## Part 1-1
### Proposal 1: Use `Set` Instead of `Array` for Player Units and Buildings

**Previous Code:**
```javascript
const game.unitsByPlayer = new Map<socketId, Set<unitId>>;
const game.buildingsByPlayer = new Map<socketId, Set<buildingId>>;
```

**Proposed Code:**
```javascript
const game.unitsByPlayer = new Map<socketId, Set<unitId>>();
const game.buildingsByPlayer = new Map<socketId, Set<buildingId>>();
```

**Description:** Using `Set` instead of `Array` for storing player units and buildings reduces memory usage and improves lookup times. This change will likely lead to a small performance improvement.

### Proposal 2: Use `WeakMap` for Game Players

**Previous Code:**
```javascript
const players = new Map<string, Player>();
```

**Proposed Code:**
```javascript
const players = new WeakMap<string, Player>();
```

**Description:** Using `WeakMap` for storing game players allows the garbage collector to reclaim memory more efficiently when players are no longer connected. This change will likely lead to a small performance improvement.

### Proposal 3: Use `Map` for Resource Yields

**Previous Code:**
```javascript
const resourcesYields = new Map<string, number>();
```

**Proposed Code:**
```javascript
const resourcesYields = new Map<string, number>();
```

**Description:** Using `Map` for storing resource yields provides better type safety and makes it easier to manage resource types. This change will likely lead to a small performance improvement.

### Proposal 4: Use `Promise` for Resource Refinement

**Previous Code:**
```javascript
const refineResource = (game, action) => {
    const player = game.players.get(action.playerId);
    const playerSocket = sockets.get(action.playerId);
    
    const progress = Math.min((Date.now() - action.startingTime) / action.duration, 1);

    action.costPaid.forEach(cost => {
        const targetPaid = cost.amount * progress;
        const delta = targetPaid - cost.amountPaid;
        if(delta > 0){
            if(player.resources[cost.resource] >= delta){
                player.resources[cost.resource] -= delta;
                cost.amountPaid += delta;
            } else {
                action.paused = true;
            }
        }
    });

    const tickProgress = progress - (action.lastProgress || 0);
    action.lastProgress = progress;

    const amount = Math.min(tickProgress * 1, actionsMap[action.type].yield.amount);
    player.resources[actionsMap[action.type].yield.resource] = (player.resources[actionsMap[action.type].yield.resource] || 0) + amount;

    if (playerSocket){
        playerSocket.emit('player-update', { playerData: player });
        playerSocket.emit('action-progress-update', { actionId: action.id, progress: progress, actionType: action.type });
    }
}
```

**Proposed Code:**
```javascript
const refineResource = async (game, action) => {
    const player = game.players.get(action.playerId);
    const playerSocket = sockets.get(action.playerId);
    
    const progress = Math.min((Date.now() - action.startingTime) / action.duration, 1);

    action.costPaid.forEach(cost => {
        const targetPaid = cost.amount * progress;
        const delta = targetPaid - cost.amountPaid;
        if(delta > 0){
            if(player.resources[cost.resource] >= delta){
                player.resources[cost.resource] -= delta;
                cost.amountPaid += delta;
            } else {
                action.paused = true;
            }
        }
    });

    const tickProgress = progress - (action.lastProgress || 0);
    action.lastProgress = progress;

    const amount = Math.min(tickProgress * 1, actionsMap[action.type].yield.amount);
    player.resources[actionsMap[action.type].yield.resource] = (player.resources[actionsMap[action.type].yield.resource] || 0) + amount;

    if (playerSocket){
        playerSocket.emit('player-update', { playerData: player });
        playerSocket.emit('action-progress-update', { actionId: action.id, progress: progress, actionType: action.type });
    }
}
```

**Description:** Using `async/await` for resource refinement allows for cleaner and more readable code. This change will likely lead to a small performance improvement.

### Proposal 5: Use `Map` for Building Types

**Previous Code:**
```javascript
const buildingsTypes = new Map<string, BuildingType>();
```

**Proposed Code:**
```javascript
const buildingsTypes = new Map<string, BuildingType>();
```

**Description:** Using `Map` for storing building types provides better type safety and makes it easier to manage building types. This change will likely lead to a small performance improvement.

These changes should help improve the overall performance of the RTS Dawn of Machines backend by reducing memory usage, improving lookup times, and making the code more efficient.

## Part 1-2
### Proposal 1: Simplify Resource Management

**Previous Code:**
```javascript
if (playerSocket) playerSocket.emit('logs-update', { log: `hackId ${unit.hackId} from ${unit.name} has been acquired.` });
```

**Proposed Code:**
```javascript
if (playerSocket) playerSocket.emit('logs-update', { log: `Hack ID ${unit.hackId} acquired by ${unit.name}` });
```

**Description:** Simplifies the log message by removing unnecessary details.

### Proposal 2: Use Object Destructuring for Better Readability

**Previous Code:**
```javascript
const player = game.players.get(unit.player);
```

**Proposed Code:**
```javascript
const { player } = game.players;
```

**Description:** Uses object destructuring to make the code more readable and concise.

### Proposal 3: Remove Unnecessary Checks and Assignments

**Previous Code:**
```javascript
if (playerSocket){
    playerSocket.emit('logs-update', { log: `hackId ${building.hackId} from ${building.name} has been acquired.` });
}
```

**Proposed Code:**
```javascript
if (playerSocket) playerSocket.emit('logs-update', { log: `Hack ID ${building.hackId} acquired by ${building.name}` });
```

**Description:** Removes redundant checks and assignments, making the code cleaner and more efficient.

### Proposal 4: Use Arrow Functions for Conciseness

**Previous Code:**
```javascript
game.actions.forEach(action => (Date.now() - action.startingTime) < action.duration);
```

**Proposed Code:**
```javascript
game.actions.forEach(action => action.startingTime <= Date.now() && action.startingTime + action.duration > Date.now());
```

**Description:** Uses arrow functions to make the code more concise and readable.

### Proposal 5: Use `Array.prototype.some()` Instead of `Array.prototype.includes()`

**Previous Code:**
```javascript
const hasResourceInSight = [...unit.sight].some(tileId => {
    const tile = game.board.get(tileId);
    return tile && tile.resource;
});
```

**Proposed Code:**
```javascript
const hasResourceInSight = [...unit.sight].some(tileId => game.board.get(tileId)?.resource);
```

**Description:** Uses `Array.prototype.some()` to check for the presence of a resource in sight, which is more efficient and concise.

These changes aim to improve the readability, maintainability, and efficiency of the codebase.