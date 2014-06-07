#include <cstdio>
#include <cstring>
#include <cmath>
#include <algorithm>
#include <vector>
using namespace std;

#define FOR(it, c) for(__typeof((c).begin()) it = (c).begin(); it != (c).end(); it++)
#define SZ(c) ((int)(c).size())

const int N = 100005;
int a[N][10], na[N];
int n, m;
vector<int> da, db;
int deg[N];

int main(void) {
    scanf("%d%d", &n, &m);
    for(int i=0;i<m;i++) {
        int x, y;
        scanf("%d%d", &x, &y);
        a[x][na[x]++] = y;
        a[y][na[y]++] = x;
    }
    int dsum=0;
    for(int i=1;i<=n;i++) dsum += min(2, n-1-na[i]);
    if(dsum/2<m) { puts("-1"); return 0; }


    if(n<=9) {
        int b[10]={};
        for(int i=1;i<=n;i++) b[i-1] = i;
        b[n] = b[0];
        int r[10][10]={};
        for(int i=1;i<=n;i++) for(int j=0;j<na[i];j++) r[i][a[i][j]] = 1;
        do {
            int fail=0;
            for(int i=0;i<m;i++) if(r[b[i]][b[i+1]]) fail=1;
            if(!fail) {
                for(int i=0;i<m;i++) printf("%d %d\n", b[i], b[i+1]);
                return 0;
            }
        } while(next_permutation(b, b+n));
        puts("-1");
        return 0;
    }


    for(int i=1;i<=n;i++) {
        da.push_back(i);
    }
    vector<pair<int, int> > ans;
    for(int T=0,c=0;T<2 && c<m;T++) {
    for(int i=1;i<=n&&c<m;i++) {
        if(deg[i]>=2) continue;
        for(int j=0;j<SZ(da);j++) if(deg[da[j]]>=2) {
            swap(da[j], da[SZ(da)-1]);
            da.pop_back();
            j--;
        } else if(da[j]!=i && da[j]!=a[i][0]&&da[j]!=a[i][1]&&da[j]!=a[i][2] &&da[j]!=a[i][3]) {
            ans.push_back(make_pair(i, da[j]));
            ++deg[i]; ++deg[da[j]];
            a[i][na[i]++] = da[j];
            a[da[j]][na[da[j]]++] = i;
            ++c;
            break;
            }
        }
    }
    //FOR(it, ans) printf("%d %d\n", it->first, it->second);
    if(SZ(ans)<m) puts("-1");
    else {
        FOR(it, ans) printf("%d %d\n", it->first, it->second);
    }
    return 0;
}
