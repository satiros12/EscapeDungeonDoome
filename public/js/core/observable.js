class Observable {
    constructor() {
        this.observers = new Set();
    }

    subscribe(observer) {
        this.observers.add(observer);
        return () => this.unsubscribe(observer);
    }

    unsubscribe(observer) {
        this.observers.delete(observer);
    }

    notify(event) {
        this.observers.forEach(observer => {
            if (observer.onEvent) {
                observer.onEvent(event);
            } else if (typeof observer === 'function') {
                observer(event);
            }
        });
    }

    clear() {
        this.observers.clear();
    }
}
