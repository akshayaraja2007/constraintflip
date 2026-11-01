#include <bits/stdc++.h>
using namespace std;

struct Edge { int to; long long w; };

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m, src;
    cin >> n >> m >> src;
    vector<vector<Edge>> g(n + 1);
    vector<int> indeg(n + 1, 0);
    for (int i = 0; i < m; ++i) {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        g[u].push_back({v, w});
        ++indeg[v];
    }

    queue<int> q;
    for (int i = 1; i <= n; ++i) if (indeg[i] == 0) q.push(i);

    vector<int> topo;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        topo.push_back(u);
        for (auto &e : g[u]) {
            --indeg[e.to];
            if (indeg[e.to] == 0) q.push(e.to);
        }
    }

    const long long INF = (1LL << 62);
    vector<long long> dist(n + 1, INF);
    dist[src] = 0;
    for (int u : topo) {
        if (dist[u] == INF) continue;
        for (auto &e : g[u]) {
            if (dist[e.to] > dist[u] + e.w) {
                dist[e.to] = dist[u] + e.w;
            }
        }
    }

    for (int i = 1; i <= n; ++i) {
        if (dist[i] == INF) cout << "UNREACHABLE\n";
        else cout << dist[i] << '\n';
    }
    return 0;
}
