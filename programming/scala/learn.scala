/**
 * MIT License
 *
 * Copyright (c) 2019 DHacky
 */

// see how the scala is compiling
//1. scala -Xprint:parse learn.scala
//2. scalac learn.scala && javap learn

object learn {
	def str() {
		// scala strings
		// String StringOps StringLike
		var s = "hello scala"
		for ( c <- s) println(c) // implement by foreach
		s.foreach(println)
		s.getBytes().foreach(println)
		println(s.filter(_!='l')) //heo scaa
		println(s.drop(6).take(5).capitalize) //Scala
		println(s.map(_.toUpper))

		var num = 886
		println(s"${s} $num")
		var retio = 0.8
		println(f"${s} ${retio}%.2f")

		var pattern = "[0-9]+".r
		println(pattern.findFirstIn(s)) //None, may return Option Some/None

		implicit class StringU(s:String) {
			def add = s.map(c=>(c+1).toChar)
			def toIntw(radix:Int) = Integer.parseInt(s, radix)
		}
		println(s.add) // real magic!!!
		println("345".toInt)
		println("f0f0".toIntw(16))
		println("10101".toIntw(2))
	}

	def control() {
		var x = if (1<3) 4 else 5
		println(x)
		for ((v, i) <- (1 to 10).zipWithIndex) {
			println(s"$i is $v")
		}
		val mm = Map(23->"one", 45->"two")
		for ((k, v) <- mm) println(s"$k $v")
		for (i <- 1 to 10 if i%2==0) println(i)

		var i = 8
		i match {
			case 1 => println(1)
			case 2 | 3 | 4 => println(s"haha $i")
			case a if 5 to 10 contains a => println(s"hehe $i")
			case _ => println("unexpected")
		}

		import util.control.Breaks._
		breakable {
			for (i <- 1 to 10) {
				if (i > 4) break
			}
		}
	}

	def cls() {
		val p = new Person(1, "scala")
		p.age = 15
		println(p)
		var pp = People("scala")
		println(pp)
	}
}

class Person(val id:Int, var name:String, var race:String="yellow") {
	var age = 18
	private val HOME = System.getProperty("user.home")
	// name and age have getter and setter
	// id has getter no setter
	// HOME has no getter and setter
	def this(name :String){
		this(Person.ID, name) // weird! I prefer this.ID
	}
	def printHome { println(s"This is my home $HOME") }
	printHome
	override def toString = s"$name is #$id, $race race, and $age years old"
}

object Person{
	val ID = 1
}

// default attributes is read only (val)
// default functions: toString unapply equals hashCode copy
case class People(var name :String)

object learn {
	//try Command Line Interface tools
	//https://github.com/jstrachan/scopt
	//https://github.com/backuity/clist
	def main(args: Array[String]) = {
		var cmd = if (args.length < 1) "null" else args(0)
		cmd match {
			case "str" => learn.str()
			case "ctl" => learn.control()
			case "cls" => learn.cls()
			case opps => println(s"unsupport $opps, <str|ctl|cls>")
		}
	}
}
