#include <cstdio>

namespace foo {
    class B {
    public:
        void testing() {
            printf("foo::B::testing()\n");
        }
    };
}

int main() {
    foo::B b;
    b.testing();
    return 0;
}
