import * as vscode from 'vscode';

// ExtensionContext单例
export class Context {
	private static instance: Context;
	private context: vscode.ExtensionContext | undefined;

	private constructor() { }

	public static getInstance(): Context {
		if (!Context.instance) {
			Context.instance = new Context();
		}
		return Context.instance;
	}

	public static set(context: vscode.ExtensionContext): void {
		Context.getInstance().context = context;
	}

	public static get(): vscode.ExtensionContext {
		const ins = Context.getInstance()
		if (!ins.context) {
			throw new Error('Extension context is not initialized');
		}
		return ins.context;
	}
}
