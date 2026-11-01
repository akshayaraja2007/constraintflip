#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long n, k;
    cin >> n >> k;
    vector<long long> a(n);
    for (long long i = 0; i < n; ++i) cin >> a[i];

    map<long long, long long> freq;
    long long prefix = 0, ans = 0;
    freq[0] = 1;
    for (long long x : a) {
        prefix += x;
        ans += freq[prefix - k];
        ++freq[prefix];
    }
    cout << ans << '\n';
    return 0;
}
