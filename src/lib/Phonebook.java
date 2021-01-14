package lib;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.InputMismatchException;
import java.util.Iterator;
import java.util.Scanner;
import java.util.Set;


/**
 * @�ۼ��� : �赿��
 * @�ۼ��� : 2020. 12. 15.
 * @filename : Phonebook.java
 * @package : lib
 * @description : �ڵ��� ����ó�� �����ϴ� ��ȭ��ȣ�� �������α׷� �Դϴ�.
 */
public class Phonebook {
	
	HashMap<String, Person> phoneBookList = new HashMap<String,Person>();
	ArrayList<Person> search_list = new ArrayList<Person>(); 
	// search �� ������ �ֱ� ���� �׸�.
	
	// 0. �޴� ��� ���
	public void printMenu() {	
		System.out.println("===========================");
		System.out.println("       ���� �޴� �� �ϳ��� �����ϼ���.");
		System.out.println("===========================");
		System.out.println("1. ȸ�� �߰�");
		System.out.println("2. ȸ�� ��� ����");
		System.out.println("3. ȸ�� ���� �����ϱ�");
		System.out.println("4. ȸ�� ����");
		System.out.println("5. ����");
	}
	
	// 1. ���� Ȯ�� ���(��ȭ��ȣ�� ������ ����,ģ��,��Ÿ���� Ȯ��)
	public boolean groupChecker(String groupName) {
		return ((groupName).matches("����"))
				|| (groupName.matches("ģ��"))
				|| (groupName.matches("��Ÿ"));
	}
	
	// 2. ��ȭ��ȣ�� �ڵ��� ��ȣ �Ǵ� ����ȭ���� �����ϴ� ���.
	public boolean numberChecker(String number) {
		if(number.length() < 10) {
			return false;
		}
		boolean phoneNumberChecker;
		 boolean elevenCheck = (((number).length())==11); // 11�ڸ����� üũ 
		 boolean frontThreeCheck = ((number.substring(0, 3)).matches("010")); // �տ� ���ڸ� �ڵ��� ��ȣ(010)���� üũ
		 boolean allDigitCheck = true;
		 char[] numberArray = number.toCharArray();
		 boolean normalNumberChecker;
		 ArrayList<String> localNumber = new ArrayList<String>();	// ������ȣ �迭�� �����Ѵ�.
		 localNumber.add("02");
		 localNumber.add("031");
		 localNumber.add("032");
		 localNumber.add("033");
		 localNumber.add("041");
		 localNumber.add("042");
		 localNumber.add("043");
		 localNumber.add("044");
		 localNumber.add("051");
		 localNumber.add("052");
		 localNumber.add("053");
		 localNumber.add("054");
		 localNumber.add("055");
		 localNumber.add("061");
		 localNumber.add("062");
		 localNumber.add("063");
		 localNumber.add("064");
		 
		 boolean tenCheck = ((number.length())==10); // ����ȭ�� 10�ڸ�
		 boolean frontThreeLocalCheck;				// �տ� ������ȣ 2�ڸ� �Ǵ� 3�ڸ� Ȯ��
		 if(((number.substring(0, 2)).matches("02"))||(localNumber.contains(number.substring(0, 3)))){
			 frontThreeLocalCheck = true;
		 }else {
			 frontThreeLocalCheck = false;
		 } // ������ȣ�� �޾Ƶ��̱�.
		 
		 localNumber.contains(number.substring(0, 3)); 
				 
		 for (char alphabet : numberArray) {
			 if(!Character.isDigit(alphabet)) {
				 allDigitCheck = false;
				 break;
			 }
		 }
		 
		 phoneNumberChecker = elevenCheck&&frontThreeCheck&&allDigitCheck; // �ڵ�����ȣ���� ����
		 normalNumberChecker = tenCheck&&frontThreeLocalCheck&&allDigitCheck; // ����ȭ��ȣ���� ����
		 
		 return phoneNumberChecker||normalNumberChecker; // 11 �����̸�, �տ� 3�ڸ��� �ڵ�����ȣ, �׸��� ��� ������ ��츸 true �̴�.
	}
	
	// 3. ����ó �߰� ���
	public void addPhoneNumber(Scanner scanner) {	// ȸ�� �߰� ��� (Ű������ ����� �ȿ� �־��ش�.)
		String name;
		String phoneNumber;
		String address;
		String group;
		Person person;
		
		System.out.println("\n����� ȸ���� ������ �Է��ϼ���.");
		System.out.print("�̸�: ");
		name = scanner.nextLine();
		
		while(true) {
			System.out.print("����ó(ex: 01023233232 �Ǵ� 0312442858): ");
			if(numberChecker(phoneNumber=scanner.nextLine())) 
							// 010,011,018 �� �����ϴ� �͸� �޾Ƶ��δ�.
			{
				break;
			}
		} // ����ó�� ���̰� 11�̰�, 010/011/018 �� �����ϴ� �͵鸸 �޾Ƶ��δ�.
		
		System.out.print("�ּ�: ");
		address = scanner.nextLine();
		while(true) {
			System.out.print("����(ex.����, ģ��, ��Ÿ): ");
			if(groupChecker(group = scanner.nextLine())) {
				break;
			}
			
		}
//		3-1. ���� ����� ���.
		if(phoneBookList.keySet().contains(phoneNumber)){
			System.out.println(phoneBookList.get(phoneNumber).toString());
			System.out.println("������ ����ó�� ����Ǿ� �ִ� ȸ���� �̹� �����մϴ�.\n������ ������ ���� ����ðڽ��ϱ�? Y/N");
			String choice=scanner.nextLine();
			if(choice.matches("Y")||choice.matches("y")) {
				System.out.println("������ ȸ���� ������ ���ŵǾ����ϴ�.");
				person = new Person(name, phoneNumber, address, group);
				phoneBookList.put(person.getPhoneNumber(), person);
			}else if(choice.matches("N")||choice.matches("n")) {
				System.out.println("������ ȸ���� ������ �������� �ʰ� ���� �޴��� ���ư��ϴ�.");
			}else {
				System.out.println("Ű�� �߸� �Է��ϼ̽��ϴ�.\n Y �Ǵ� N ���� �ٽ� �������ּ���.");
			}
		}else {
			person = new Person(name, phoneNumber, address, group);
			phoneBookList.put(person.getPhoneNumber(), person);
			System.out.println("\n����� �Ϸ�Ǿ����ϴ�.\n");
		}
			
	}
	
	// 4. ȸ�� ��� ���� ���
	public void showList() {
		Set<String> set = phoneBookList.keySet();
		Iterator<String> it =set.iterator();
		System.out.println("\n�� "+phoneBookList.size()
		 				  +" ���� ȸ���� ����Ǿ� �ֽ��ϴ�.");
		while(it.hasNext()) {
			String phoneNumber = it.next();
			Person person = phoneBookList.get(phoneNumber);
			System.out.print("ȸ������ - "+person.toString());
			System.out.println();
		}
		
	}
	
	
	// 5. ȸ�� ���� �����ϱ� ���
	public void editPerson(Scanner scanner) {
		if(!phoneBookList.isEmpty()) {
			while(true) {
				System.out.println("\n������ ȸ���� �̸��� �Է��ϼ���.");
				searchFunction(scanner); 
//				�� �̸��� �ش��ϴ� ȸ���� �������� ������ �޴��� ���ư�.
				if(search_list.size()==0) {
					break;
				}
				
				
				while(true) {
					System.out.println("�Ʒ� ��� �� ������ ȸ���� ��ȣ�� �Է��ϼ���. \n(0���� �Է��Ͻø� ���θ޴��� ���ư��ϴ�.)");
					for(int i=0; i<search_list.size(); i++) {
						Person person = search_list.get(i);
						System.out.println((i+1)+"."+person.toString());
					}
					
					
					int choice;
					
//				��Ͽ� �ִ� ȸ�� ���� ���� ������ �� �������ִ� ���α׷�.
//				InputMismatch exception �ذ� �Ϸ�.
					try {
						while(((choice = scanner.nextInt()-1)>=search_list.size())||(choice < -1)) {
							System.out.println("������ ���� ��ȿ���� �ʽ��ϴ�. ������ ȸ���� ��ȣ�� �ٽ� �Է����ּ���.\n0���� �����ø� ���θ޴��� ���ư��ϴ�.");
						}
						scanner.nextLine();
						// ���⼭ �Է¹޴� ���ڰ� �ε��� ���ں��� �۵��� �����Ϸ� 
						// ���࿡ �ε��� ���ں��� ũ�� ���� ���� ����Ǹ� �ȵ�.
						if(choice==-1) {
							System.out.println("���� �޴��� �̵��մϴ�.\n");
							search_list.clear();
							break;
						}
						
						System.out.println("������ ������ �Է��ϼ���.");
						System.out.print("�̸�: ");
						String edited_name = scanner.nextLine();
						String edited_phoneNumber;
						
//					�ڵ�����ȣ �Ǵ� ����ȭ���� �ƴϸ� �ٽ� ����ó�� �޵��� ������.
						while(true) { 
							System.out.print("����ó(ex: 01023233232 �Ǵ� 0312442858): ");
							if(numberChecker(edited_phoneNumber=scanner.nextLine())) 
								// �ڵ��� ��ȣ �Ǵ� ����ȭ��ȣ ���ĸ� �޾Ƶ��δ�.
							{
								break;
							}
						}
						
//					�ּ� ���� - �����ϴ°� ���� ����.
						System.out.print("�ּ�: ");
						String edited_address = scanner.nextLine();
						String edited_group;
						
//					������ �Է��� ��, ����,ģ��,��Ÿ �� ������ �̿��� ���� �־��� �� �ٽ� �Է��ϵ��� ����.
						while(true) {
							System.out.print("����(ex.����, ģ��, ��Ÿ): ");
							if(groupChecker(edited_group = scanner.nextLine())) { 
								// ������ ���� ģ�� ��Ÿ �� ���������� �ƴ��� �����Ѵ�.
								break;
							}
						}
						
//						�ߺ��� ����� ������ Ȯ���ϴ� ���.
						if(phoneBookList.keySet().contains(edited_phoneNumber)){
							System.out.println(phoneBookList.get(edited_phoneNumber).toString());
							System.out.println("������ ����ó�� ����Ǿ� �ִ� ȸ���� �̹� �����մϴ�.\n������ ������ ���� ����ðڽ��ϱ�? Y/N");
							String choice2=scanner.nextLine();
							if(choice2.matches("Y")||choice2.matches("y")) {
								phoneBookList.remove(search_list.get(choice).getPhoneNumber());
								search_list.get(choice).setName(edited_name); 
								search_list.get(choice).setPhoneNumber(edited_phoneNumber);
								search_list.get(choice).setAddress(edited_address);
								search_list.get(choice).setGroup(edited_group);
								phoneBookList.put(search_list.get(choice).getPhoneNumber(), search_list.get(choice));
								System.out.println("\n������ �Ϸ�Ǿ����ϴ�.\n");
								search_list.clear();
								break;	
							}else if(choice2.matches("N")||choice2.matches("n")) {
								System.out.println("\n������ ȸ���� ������ �������� �ʰ� ���� �޴��� ���ư��ϴ�.\n");
								search_list.clear();
								break;
							}else {
								System.out.println("Ű�� �߸� �Է��ϼ̽��ϴ�.\n Y �Ǵ� N ���� �ٽ� �������ּ���.");
								search_list.clear();
							}
						}else {
//							�������� ���� ���� �̸�, ��ȭ��ȣ, �ּ�, ������ ���� ��´�.
							phoneBookList.remove(search_list.get(choice).getPhoneNumber());
							search_list.get(choice).setName(edited_name); 
							search_list.get(choice).setPhoneNumber(edited_phoneNumber);
							search_list.get(choice).setAddress(edited_address);
							search_list.get(choice).setGroup(edited_group);
							phoneBookList.put(search_list.get(choice).getPhoneNumber(), search_list.get(choice));
							search_list.clear();
							System.out.println("\n������ �Ϸ�Ǿ����ϴ�.\n");
							break;	
						}		
					}catch(InputMismatchException e) {
						scanner.nextLine();
						System.out.println("���ڸ� �Է����ּ���.");
						continue;
					}
				}
				break;
			}			
			}else {
//			��Ͽ� ����ó�� �ϳ��� ���� ���� �ٽ� �ʱ�޴��� ���ư�.
			System.out.println("\n������ �� �ִ� ȸ���� �����ϴ�.\n");
		}		
	}
	
	// 6. �˻��ϴ� ���
	public void searchFunction(Scanner scanner) {
		System.out.print("�̸� : ");
		String name = scanner.nextLine();
//		�̸� �޾� �鿴��, ���� ã�Ƴ��� ��.
//		���� HashMap �ݺ��� ������, �̸��� �� �̸��̸� search_list �� �߰��ؾ� ��.
		Set<String> phoneNumbers = phoneBookList.keySet();
		Iterator<String> it = phoneNumbers.iterator();
		while (it.hasNext()) {
			Person person = phoneBookList.get(it.next());
			if (person.getName().matches(name)) {
				search_list.add(person); // �˻��� �̸��� �ش��ϴ� ����� ������ ArrayList �� ����.
			}
		}
		if(search_list.size()==0) {
			System.out.println("\n�ش��ϴ� ȸ�� ������ �����ϴ�.\n");
			return;
		}else {
			System.out.println("�� "+ search_list.size() + "���� ����� �˻��Ǿ����ϴ�.");			
		}
	}
	
	
	// 7. ȸ�� ���� ���
	public void removePerson(Scanner scanner) {
//		��ȭ��ȣ�ο� ��� �Ѹ��̶� ���� �� ���� �ܰ�� �Ѿ��.
		if(!phoneBookList.isEmpty()) {
			System.out.println("\n������ ȸ���� �̸��� �Է��ϼ���.");			
			searchFunction(scanner);
			
			if(search_list.size()==0) {
				return;
			}
			
			while(true) {
				System.out.println("�Ʒ� ��� �� ������ ȸ���� ��ȣ�� �Է��ϼ���. \n(������ ������ ���� ��� 0���� �Է����ּ���.)");			
				if(!search_list.isEmpty()) { 
					for(int i=0; i<search_list.size(); i++) {
						Person person = search_list.get(i);
						System.out.println((i+1)+"."+person.toString());						 
					} 
//					InputMismatchException ó�� �Ϸ�.
					try {
						int choice;
						while(((choice = scanner.nextInt()-1)>=search_list.size())||(choice < -1)) {
							System.out.println("������ ���� ��ȿ���� �ʽ��ϴ�. ������ ȸ���� ��ȣ�� �ٽ� �Է����ּ���.\n0���� �����ø� ���θ޴��� ���ư��ϴ�.");
						}
						scanner.nextLine();
						if(choice == -1) {
							System.out.println("\n���� �޴��� ���ư��ϴ�.\n");
							search_list.clear();
							break;
						}
//						�ε��� ���� �Ѿ�°� ����ó�� �Ϸ�.
						try {
							phoneBookList.remove(search_list.get(choice).getPhoneNumber());
							System.out.println("\n�ش� ȸ���� ����ó�� �����Ǿ����ϴ�.\n");
							search_list.clear(); // ����� ���� �ʿ䰡 ������ �ʱ�ȭ�� �����ش�.
							break;
						}catch(IndexOutOfBoundsException e) {						
							System.out.println("������ ���� ��ȿ���� �ʽ��ϴ�. \n������ ȸ���� ��ȣ�� �ٽ� �Է����ּ���.");
						}					
//					���ڰ� �ƴ� ��ǲ ���� ó��. (int choice (������ ��))
					}catch(InputMismatchException e) {
						scanner.nextLine();
						System.out.println("���ڸ� �Է����ּ���.");
						continue;
					}
				}else {
//					�˻� ����Ʈ�� ���� �˻��ϴ� �̸��� ������ ���θ޴��� ���ư���.
					System.out.println("\n�˻��Ͻ� �̸��� ã�� �� �����ϴ�.\n");
					break;
				}
			}
		}else { // ��Ͽ� ����ó�� �ϳ��� ���� �� ���θ޴��� ���ư���.
			System.out.println("\n������ �� �ִ� ȸ���� �����ϴ�.\n");			
		}
	}	
}

// rrrrrrrrrrrrrrrrrr
// 패치패치
