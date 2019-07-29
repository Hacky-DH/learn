#include<new> // new_handler set_new_handler
#include<memory>
#include<iostream>

using std::new_handler;

// all global operator new:
// void* operator new(std::size_t);
// void* operator new(std::size_t, void*) noexcept;
// void* operator new(std::size_t, const std::nothrow_t&) noexcept;

// new_hander RAII
class NewhandlerHolder {
	new_handler handler;
public:
	explicit NewhandlerHolder(new_handler h): handler(h) {}
	~NewhandlerHolder(){
		std::set_new_handler(handler);
	}
	NewhandlerHolder(const NewhandlerHolder&) = delete;
	NewhandlerHolder& operator=(const NewhandlerHolder&) = delete;
};

// base class that support setting class-owned new_handler
// use template to sparate static members from each classes
template<typename T>
class Newhandler {
	static new_handler current_handler;
public:
	static new_handler set_new_handler(new_handler) noexcept;
	static void* operator new(std::size_t);
	static void operator delete(void*) noexcept;
};

template<typename T>
new_handler Newhandler<T>::current_handler = nullptr;

template<typename T>
new_handler Newhandler<T>::set_new_handler(new_handler handler) noexcept {
	new_handler o = current_handler;
	current_handler = handler;
	return o;
}

template<typename T>
void* Newhandler<T>::operator new(std::size_t size) {
	NewhandlerHolder h(std::set_new_handler(current_handler));
	std::cout<<"call class-owned operator new"<<std::endl;
	return ::operator new(size);
}

template<typename T>
void Newhandler<T>::operator delete(void* ptr) noexcept {
	std::cout<<"call class-owned operator delete"<<std::endl;
	return ::operator delete(ptr);
}

void outOfMem() {
	std::cerr<<"out of memory"<<std::endl;
	std::abort();
}

// test class
class Widget: public Newhandler<Widget> {
public:
	// let super new and delete visible
	using Newhandler<Widget>::operator new;
	using Newhandler<Widget>::operator delete;
	// placement new and delete
	static void* operator new(std::size_t, std::ostream&);
	// call this when exception in constructor
	static void operator delete(void*, std::ostream&) noexcept;
};

void* Widget::operator new(std::size_t size, std::ostream& out) {
	out<<"call class-owned placement operator new"<<std::endl;
	return ::operator new(size);
}

void Widget::operator delete(void* ptr, std::ostream& out) noexcept {
	out<<"call class-owned placement operator delete"<<std::endl;
	return ::operator delete(ptr);
}

int main()
{
	Widget::set_new_handler(outOfMem);
	std::shared_ptr<Widget> pw(new Widget);
	Widget *ppw = new (std::cerr) Widget;
	delete ppw;
	return 0;
}
