package lib;


/**
 * @�ۼ��� : �赿��
 * @�ۼ��� : 2020. 12. 15.
 * @filename : Person.java
 * @package : lib
 * @description : ����� ���������� ��� Ŭ�����Դϴ�.
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
		// 불필요한 함수를 지웁니다.
		return group;
	}

	public void setGroup(String group) {
		this.group = group;
	}
	
	@Override
		public String toString() {
			return "�̸� : "+ this.name+", ��ȭ��ȣ : "+ this.phoneNumber+", �ּ� : "
					   + this.address+ ", ���� : "+ this.group;
		}
	
	
	

}
