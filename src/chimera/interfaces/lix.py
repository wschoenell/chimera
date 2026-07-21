import json
import urllib.parse
import urllib.request


def get_object_info(object_name):
    # based on https://gist.github.com/daleghent/2d80fffbaef2f1614962f0ddc04bee92
    url = "https://simbad.u-strasbg.fr/simbad/sim-tap/sync"
    query = f"""
    SELECT basic.OID, main_id, RA, DEC
    FROM basic
    JOIN ident ON oidref = oid
    WHERE id = '{object_name}'
    """
    data = urllib.parse.urlencode(
        {"query": query, "format": "json", "lang": "ADQL", "request": "doQuery"}
    ).encode("utf-8")

    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req) as response:
        if response.status != 200:
            raise Exception(f"HTTP Error: {response.status}")
        out = json.load(response)

    oid = out["data"][0][0]
    main_id = out["data"][0][1]
    ra = out["data"][0][2]
    dec = out["data"][0][3]

    result = {
        "simbad_oid": oid,
        "main_id": main_id,
        "ra": ra,
        "dec": dec,
    }

    return result
