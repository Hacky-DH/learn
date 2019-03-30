// newton
// evaluate the root of 5x^3-8x^2+3x-6=0
// f'(x) = f(x0)/(x1-x0)

#include <stdio.h>
#include <math.h>

static double e = 1e-6;

double newton(double start_value, int max_epoch) {
	double value, derivative, new_value;
	int i = 0;
	do{
		value = 5*start_value*start_value*start_value
			- 8*start_value*start_value + 3*start_value - 6;
		derivative = 15*start_value*start_value - 16*start_value + 3;
		new_value = start_value - value/derivative;
		start_value = new_value;
		++i;
	}while(i < max_epoch && fabs(start_value-new_value) < e);
	return new_value;
}

int main() {
	printf("%f\n", newton(0, 50));
}