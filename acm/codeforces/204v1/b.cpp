/* --- Author: Vladimir Smykalov, enot.1.10@gmail.com --- */
#include <iostream>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <cstring>
#include <cmath>
#include <algorithm>
#include <vector>
#include <set>
#include <map>
#include <ctime>
#include <cassert>

using namespace std;

#define fs first
#define sc second
#define pb push_back
#define mp make_pair
#define range(i, n) for (int i=0; i<(n); ++i)
#define forit(it,v) for(typeof((v).begin()) it = v.begin() ; it != (v).end() ; ++it)
#define eprintf(...) fprintf(stderr, __VA_ARGS__),fflush(stderr)
#define sz(a) ((int)(a).size())
#define all(a) (a).begin(),a.end()

typedef long long ll;
typedef vector<int> VI;
typedef pair<int, int> PII;

int main() {
#ifndef ONLINE_JUDGE
    freopen("b.in", "r", stdin);
#endif
    int n;
    cin >> n;
    vector<int> arr;
    range(i, n) {
        int val;
        cin >> val;
        arr.pb(val);
    }
    int cnt = 0;
    while (true) {
        bool found = false;
        range(i, n) {
            if (i && arr[i] < arr[i - 1]) {
                swap(arr[i], arr[i - 1]);
                cnt ++;
                found = true;
            }
        }
        if (!found) break;
    }
    double ans = 0.0;
    if (cnt <= 1) {
        ans = cnt;
    } else {
        if (cnt % 2 == 1) {
            ans += cnt * 2 - 1;
        } else {
            ans +=  cnt * 2;
        }
    }

    printf("%.6lf\n", ans);

    return 0;
}
