from Tests.TestLogger import logger

def getItemsByContainmentTree(mdib, ctp):
    try:
        codes = ctp.split(".")
        handles = {mds.handle for mds in mdib.descriptions.codeId.get(codes[0], [])}
        for code in codes[1:]:
            children = mdib.descriptions.codeId.get(code, [])
            children = [c for c in children if c.parentHandle in handles]
            handles = {c.handle for c in children}
        logger.info("Found handles %s for containment tree path %s", handles, ctp)
        return handles
    except:
        logger.error("Failed to find an Mdib item by containment tree path %s", ctp)
        return None