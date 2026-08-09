export interface CachedXForm {
  id: string;
  xformXml: string;
  updatedAt: string;
}

class XFormCacheStore {
  private readonly databaseName = 'tacatdp-xform-cache';
  private readonly storeName = 'xforms';
  private readonly maxEntries = 5;

  async get(id: string): Promise<string | null> {
    const db = await this.open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(this.storeName, 'readonly');
      const request = tx.objectStore(this.storeName).get(id);
      request.onsuccess = () => {
        const cached = request.result as CachedXForm | undefined;
        resolve(typeof cached?.xformXml === 'string' ? cached.xformXml : null);
      };
      request.onerror = () => reject(request.error ?? new Error('Unable to load cached XForm.'));
      tx.oncomplete = () => db.close();
    });
  }

  async set(id: string, xformXml: string): Promise<void> {
    const db = await this.open();
    await new Promise<void>((resolve, reject) => {
      const tx = db.transaction(this.storeName, 'readwrite');
      tx.objectStore(this.storeName).put({ id, xformXml, updatedAt: new Date().toISOString() });
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error ?? new Error('Unable to save cached XForm.'));
    });
    db.close();
    await this.prune();
  }

  private async prune(): Promise<void> {
    const db = await this.open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(this.storeName, 'readwrite');
      const store = tx.objectStore(this.storeName);
      const request = store.getAll();
      request.onsuccess = () => {
        const staleRows = (request.result as CachedXForm[])
          .sort((left, right) => right.updatedAt.localeCompare(left.updatedAt))
          .slice(this.maxEntries);
        staleRows.forEach((row) => store.delete(row.id));
      };
      request.onerror = () => reject(request.error ?? new Error('Unable to prune cached XForms.'));
      tx.oncomplete = () => {
        db.close();
        resolve();
      };
      tx.onerror = () => reject(tx.error ?? new Error('Unable to prune cached XForms.'));
    });
  }

  private async open(): Promise<IDBDatabase> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.databaseName, 1);
      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains(this.storeName)) {
          db.createObjectStore(this.storeName, { keyPath: 'id' });
        }
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error ?? new Error('Unable to open XForm cache database.'));
    });
  }
}

export const xformCache = new XFormCacheStore();
