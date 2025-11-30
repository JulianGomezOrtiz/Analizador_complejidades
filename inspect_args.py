
import ast
with open("debug_args.txt") as f:
    data = f.read()
    # data is string representation of list of dicts.
    # It might not be valid python literal if it contains objects, but here it should be dicts.
    print(f"Data length: {len(data)}")
    try:
        recs = eval(data)
        print(f"Recs count: {len(recs)}")
        for r in recs:
            for arg in r['args']:
                print(f"Arg type: {arg.get('type')}")
                if arg.get('type') == 'BinOp':
                    print(f"BinOp found: {arg}")
    except Exception as e:
        print(f"Error: {e}")
