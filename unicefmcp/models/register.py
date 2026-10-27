import sys, pandas as pd
config, model, effort, repeat, *ids = sys.argv[1:]
r = pd.read_csv("runs.csv", dtype=str); n = len(r)
new = [dict(run=n+i+1, config=config, model=model, effort=effort, repeat=repeat, qid=f"Q{i//3+1}", server=["wh","un","wb"][i%3], agent_id=a) for i, a in enumerate(ids)]
assert len(ids) == 12
pd.concat([r, pd.DataFrame(new)]).to_csv("runs.csv", index=False); print(n + len(new), "runs registered")
