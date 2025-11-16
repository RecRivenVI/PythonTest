import os
import csv
import argparse
import concurrent.futures
import anvil
from pathlib import Path

def parse_region_coords(file_name):
    """
    从文件名解析区块坐标，例如 r.-1.-1.mca -> (-1, -1)
    """
    base = Path(file_name).stem  # 去掉扩展名
    parts = base.split(".")
    if len(parts) >= 3 and parts[0] == "r":
        rx, rz = int(parts[1]), int(parts[2])
        return rx, rz
    return 0, 0

def region_to_chunk_offset(rx, rz):
    """
    根据 region 坐标计算 chunk 基准坐标
    每个 region 文件包含 32x32 个 chunk
    """
    cx = rx * 32
    cz = rz * 32
    return cx, cz

def process_chunk(file_path, cx, cz, search_type, search_value, base_cx, base_cz):
    results = []
    try:
        region = anvil.Region.from_file(file_path)
        chunk = anvil.Chunk.from_region(region, cx, cz)
        for x in range(16):
            for z in range(16):
                for y in range(256):
                    block = chunk.get_block(x, y, z)
                    if block is None:
                        continue

                    if search_type == "block":
                        value = str(block)
                    elif search_type == "block.id":
                        value = block.id
                    elif search_type == "block.properties":
                        value = str(block.properties)
                    else:
                        continue

                    if str(value) == search_value:
                        # 世界坐标 = (chunk坐标 * 16 + 局部坐标)
                        world_x = (base_cx + cx) * 16 + x
                        world_y = y
                        world_z = (base_cz + cz) * 16 + z
                        tile_entity = chunk.get_tile_entity(world_x, world_y, world_z)
                        if tile_entity:
                            safe_tile_entity = {k: str(v) for k, v in tile_entity.items()}
                        else:
                            safe_tile_entity = None
                        print(f"Match in {file_path}: "
                              f"Chunk({base_cx+cx},{base_cz+cz}) "
                              f"Pos({x},{y},{z}) -> World({world_x},{world_y},{world_z}) -> {block}")
                        results.append({
                            "file": file_path,
                            "chunk_x": base_cx + cx,
                            "chunk_z": base_cz + cz,
                            "x": x,
                            "y": y,
                            "z": z,
                            "world_x": world_x,
                            "world_y": world_y,
                            "world_z": world_z,
                            "block": str(block),
                            "block.id": block.id,
                            "block.properties": block.properties,
                            "tile_entity": safe_tile_entity
                        })
    except Exception:
        pass
    return results

def main():
    parser = argparse.ArgumentParser(description="Search blocks in MCA files")
    parser.add_argument("path", help="路径（例如 \"C:\\Users\\RavenYin\\Downloads\"）")
    parser.add_argument("type", choices=["block", "block.id", "block.properties"],
                        help="搜索类型")
    parser.add_argument("value", help="匹配值")
    parser.add_argument("output", help="输出 CSV 文件名，例如 result.csv")
    args = parser.parse_args()

    base_path = Path(args.path).expanduser().resolve()

    mca_files = []
    for root, _, files in os.walk(base_path):
        for f in files:
            if f.endswith(".mca"):
                mca_files.append(os.path.join(root, f))

    all_results = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for f in mca_files:
            rx, rz = parse_region_coords(f)
            base_cx, base_cz = region_to_chunk_offset(rx, rz)

            for cx in range(32):
                for cz in range(32):
                    futures.append(
                        executor.submit(process_chunk, f, cx, cz, args.type, args.value, base_cx, base_cz)
                    )

        for future in concurrent.futures.as_completed(futures):
            all_results.extend(future.result())

    # 输出 CSV，包含世界坐标
    with open(args.output, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["file", "chunk_x", "chunk_z", "x", "y", "z",
                      "world_x", "world_y", "world_z",
                      "block", "block.id", "block.properties", "tile_entity"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

    print(f"\n搜索完成，共找到 {len(all_results)} 个匹配方块。结果已保存到 {args.output}")

if __name__ == "__main__":
    main()
