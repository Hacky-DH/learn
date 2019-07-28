// use member function templates to accept all comatible types
template<typename T>
class Rational {
	T num, den;
public:
	// allow implict type conversions
	Rational(const T& n=0, const T& d=1):num(n),den(d) {}
	const T numerator() const {return num;}
	const T denominator() const {return den;}
	friend const Rational operator*(const Rational& l, const Rational& r){
		return deMultiply(l ,r);
	}
};

template<typename T>
const Rational<T> deMultiply(const Rational<T>& l, const Rational<T>& r) {
	return Rational<T>(l.numerator()*r.numerator(), l.denominator()*r.denominator());
}

int main()
{
	Rational<int> a(1, 2);
	Rational<int> res = a * 2;
	return 0;
}
