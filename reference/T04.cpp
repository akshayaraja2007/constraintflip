#include <bits/stdc++.h>
using namespace std;

struct Fenwick {
    int n;
    vector<long long> bit;
    Fenwick(int n) : n(n), bit(n + 1, 0) {}
    void add(int idx, long long val) {
        for (int i = idx; i <= n; i += i & -i) bit[i] += val;
    }
    long long sum(int idx) const {
        long long ans = 0;
        for (int i = idx; i > 0; i -= i & -i) ans += bit[i];
        return ans;
    }
    long long rangeSum(int l, int r) const {
        return sum(r) - sum(l - 1);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;
    vector<long long> a(n + 1);
    for (int i = 1; i <= n; ++i) {
        cin >> a[i];
    }
    Fenwick fw(n);
    for (int i = 1; i <= n; ++i) fw.add(i, a[i]);

    while (q--) {
        char type;
        cin >> type;
        if (type == 'U') {
            int x;
            long long v;
            cin >> x >> v;
            fw.add(x, v - a[x]);
            a[x] = v;
        } else {
            int l, r;
            cin >> l >> r;
            cout << fw.rangeSum(l, r) << '\n';
        }
    }
    return 0;
}
