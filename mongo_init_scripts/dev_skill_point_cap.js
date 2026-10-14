// Development server: raise the skill point cap so test characters can master
// every Jedi discipline (5 trees x 89 points = 445). The original game uses 250.
// Read by SkillService and trainers via the "skillPointCap" setting (package "gameplay").
db.config.updateOne(
	{ package: "gameplay" },
	{ $set: { skillPointCap: NumberInt(1000) } },
	{ upsert: true }
);
