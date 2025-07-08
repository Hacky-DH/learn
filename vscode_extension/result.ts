// 类似rust中处理错误的方式
// 成功返回数据或失败返回error
export interface Success<T> {
	success: true;
	data: T;
}

export interface Failure {
	success: false;
	error: string;
}

export type Result<T> = Success<T> | Failure;

export function success<T>(data: T): Success<T> {
	return { success: true, data };
}

export function failure(error: string): Failure {
	return { success: false, error };
}

export function is_succ<T>(result: Result<T>): result is Success<T> {
	return result.success === true;
}

export const Result = {
	expect: <T>(result: Result<T>, errorMessage: string): T => {
		if (is_succ(result)) {
			return result.data;
		} else {
			throw new Error(`${errorMessage} ${result.error}`);
		}
	},
	get: <T>(result: Result<T>): T => {
		if (is_succ(result)) {
			return result.data;
		} else {
			throw new Error(result.error);
		}
	},
	get_or: <T>(result: Result<T>, defualt: T): T => {
		if (is_succ(result)) {
			return result.data;
		} else {
			return defualt;
		}
	}
}
