/**
 * Disjoint-Set Union (DSU / Union-Find) with Path Compression and Union by Rank
 * Used for instant live detour recovery when an active relay node depletes.
 */

export class UnionFind {
  private parent: Map<number, number> = new Map();
  private rank: Map<number, number> = new Map();
  private setSize: Map<number, number> = new Map();

  constructor(elements?: Iterable<number>) {
    if (elements) {
      for (const elem of elements) {
        this.add(elem);
      }
    }
  }

  public add(x: number) {
    if (!this.parent.has(x)) {
      this.parent.set(x, x);
      this.rank.set(x, 0);
      this.setSize.set(x, 1);
    }
  }

  public find(x: number): number {
    if (!this.parent.has(x)) {
      this.add(x);
      return x;
    }
    let p = this.parent.get(x)!;
    if (p !== x) {
      p = this.find(p);
      this.parent.set(x, p);
    }
    return p;
  }

  public union(x: number, y: number): boolean {
    const rootX = this.find(x);
    const rootY = this.find(y);
    if (rootX === rootY) return false;

    const rankX = this.rank.get(rootX) || 0;
    const rankY = this.rank.get(rootY) || 0;
    const sizeX = this.setSize.get(rootX) || 1;
    const sizeY = this.setSize.get(rootY) || 1;

    if (rankX < rankY) {
      this.parent.set(rootX, rootY);
      this.setSize.set(rootY, sizeX + sizeY);
    } else if (rankX > rankY) {
      this.parent.set(rootY, rootX);
      this.setSize.set(rootX, sizeX + sizeY);
    } else {
      this.parent.set(rootY, rootX);
      this.rank.set(rootX, rankX + 1);
      this.setSize.set(rootX, sizeX + sizeY);
    }
    return true;
  }

  public connected(x: number, y: number): boolean {
    return this.find(x) === this.find(y);
  }

  public clear() {
    this.parent.clear();
    this.rank.clear();
    this.setSize.clear();
  }
}
