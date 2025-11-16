import anvil

region = anvil.Region.from_file('r.-1.-1.mca')
chunk = anvil.Chunk.from_region(region, 11, 13)

lx, ly, lz = 1, 116, 1

block = chunk.get_block(lx, ly, lz)
print(block)
print(block.id)
print(block.properties)
nbt = chunk.get_tile_entity(-335, 116, -303)
print(nbt)