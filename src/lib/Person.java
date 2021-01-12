package lib;


/**
 * @작성자 : 김동윤
 * @작성일 : 2020. 12. 15.
 * @filename : Person.java
 * @package : lib
 * @description : 사람의 인적사항을 담는 클래스입니다.
 */
public class Person {
	private String name;
	private String phoneNumber;
	private String address;
	private String group;
	
	public Person(String name, String phoneNumber, String address, String group) {
		this.name = name;
		this.phoneNumber = phoneNumber;
		this.address = address;
		this.group = group;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getPhoneNumber() {
		return phoneNumber;
	}

	public void setPhoneNumber(String phoneNumber) {
		this.phoneNumber = phoneNumber;
	}

	public String getAddress() {
		return address;
	}

	public void setAddress(String address) {
		this.address = address;
	}

	public String getGroup() {
		return group;
	}

	public void setGroup(String group) {
		this.group = group;
	}
	
	@Override
		public String toString() {
			return "이름 : "+ this.name+", 전화번호 : "+ this.phoneNumber+", 주소 : "
					   + this.address+ ", 종류 : "+ this.group;
		}
	
	
	

}
