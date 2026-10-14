// Development server: double open-world NPC density (stock: npcSpawnChance 5, maxObservedNpcs 12).
// Read by DynamicSpawnService (package "support.npc.spawn") at startup; restart the server after changing.
db.config.updateOne(
	{ package: "support.npc.spawn" },
	{ $set: { npcSpawnChance: NumberLong(10), maxObservedNpcs: NumberLong(24) } },
	{ upsert: true }
);
