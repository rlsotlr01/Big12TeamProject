package lib;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.InputMismatchException;
import java.util.Iterator;
import java.util.Scanner;
import java.util.Set;


/**
 * @작성자 : 김동윤
 * @작성일 : 2020. 12. 15.
 * @filename : Phonebook.java
 * @package : lib
 * @description : 핸드폰 연락처를 저장하는 전화번호부 응용프로그램 입니다.
 */
public class Phonebook {
	
	HashMap<String, Person> phoneBookList = new HashMap<String,Person>();
	ArrayList<Person> search_list = new ArrayList<Person>(); 
	// search 한 값들을 넣기 위한 그릇.
	
	// 0. 메뉴 출력 기능
	public void printMenu() {	
		System.out.println("===========================");
		System.out.println("       다음 메뉴 중 하나를 선택하세요.");
		System.out.println("===========================");
		System.out.println("1. 회원 추가");
		System.out.println("2. 회원 목록 보기");
		System.out.println("3. 회원 정보 수정하기");
		System.out.println("4. 회원 삭제");
		System.out.println("5. 종료");
	}
	
	// 1. 종류 확인 기능(전화번호의 종류가 가족,친구,기타인지 확인)
	public boolean groupChecker(String groupName) {
		return ((groupName).matches("가족"))
				|| (groupName.matches("친구"))
				|| (groupName.matches("기타"));
	}
	
	// 2. 전화번호가 핸드폰 번호 또는 집전화인지 검증하는 기능.
	public boolean numberChecker(String number) {
		if(number.length() < 10) {
			return false;
		}
		boolean phoneNumberChecker;
		 boolean elevenCheck = (((number).length())==11); // 11자리인지 체크 
		 boolean frontThreeCheck = ((number.substring(0, 3)).matches("010")); // 앞에 세자리 핸드폰 번호(010)인지 체크
		 boolean allDigitCheck = true;
		 char[] numberArray = number.toCharArray();
		 boolean normalNumberChecker;
		 ArrayList<String> localNumber = new ArrayList<String>();	// 지역번호 배열을 생성한다.
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
		 
		 boolean tenCheck = ((number.length())==10); // 집전화는 10자리
		 boolean frontThreeLocalCheck;				// 앞에 지역번호 2자리 또는 3자리 확인
		 if(((number.substring(0, 2)).matches("02"))||(localNumber.contains(number.substring(0, 3)))){
			 frontThreeLocalCheck = true;
		 }else {
			 frontThreeLocalCheck = false;
		 } // 지역번호만 받아들이기.
		 
		 localNumber.contains(number.substring(0, 3)); 
				 
		 for (char alphabet : numberArray) {
			 if(!Character.isDigit(alphabet)) {
				 allDigitCheck = false;
				 break;
			 }
		 }
		 
		 phoneNumberChecker = elevenCheck&&frontThreeCheck&&allDigitCheck; // 핸드폰번호인지 검증
		 normalNumberChecker = tenCheck&&frontThreeLocalCheck&&allDigitCheck; // 집전화번호인지 검증
		 
		 return phoneNumberChecker||normalNumberChecker; // 11 숫자이며, 앞에 3자리가 핸드폰번호, 그리고 모두 숫자일 경우만 true 이다.
	}
	
	// 3. 연락처 추가 기능
	public void addPhoneNumber(Scanner scanner) {	// 회원 추가 기능 (키보드의 기능을 안에 넣어준다.)
		String name;
		String phoneNumber;
		String address;
		String group;
		Person person;
		
		System.out.println("\n등록할 회원의 정보를 입력하세요.");
		System.out.print("이름: ");
		name = scanner.nextLine();
		
		while(true) {
			System.out.print("연락처(ex: 01023233232 또는 0312442858): ");
			if(numberChecker(phoneNumber=scanner.nextLine())) 
							// 010,011,018 로 시작하는 것만 받아들인다.
			{
				break;
			}
		} // 연락처의 길이가 11이고, 010/011/018 로 시작하는 것들만 받아들인다.
		
		System.out.print("주소: ");
		address = scanner.nextLine();
		while(true) {
			System.out.print("종류(ex.가족, 친구, 기타): ");
			if(groupChecker(group = scanner.nextLine())) {
				break;
			}
			
		}
//		3-1. 덮어 씌우기 기능.
		if(phoneBookList.keySet().contains(phoneNumber)){
			System.out.println(phoneBookList.get(phoneNumber).toString());
			System.out.println("기입한 연락처로 저장되어 있는 회원이 이미 존재합니다.\n기입한 정보로 덮어 씌우시겠습니까? Y/N");
			String choice=scanner.nextLine();
			if(choice.matches("Y")||choice.matches("y")) {
				System.out.println("기입한 회원의 정보로 갱신되었습니다.");
				person = new Person(name, phoneNumber, address, group);
				phoneBookList.put(person.getPhoneNumber(), person);
			}else if(choice.matches("N")||choice.matches("n")) {
				System.out.println("기입한 회원의 정보로 갱신하지 않고 메인 메뉴로 돌아갑니다.");
			}else {
				System.out.println("키를 잘못 입력하셨습니다.\n Y 또는 N 으로 다시 기입해주세요.");
			}
		}else {
			person = new Person(name, phoneNumber, address, group);
			phoneBookList.put(person.getPhoneNumber(), person);
			System.out.println("\n등록이 완료되었습니다.\n");
		}
			
	}
	
	// 4. 회원 목록 보기 기능
	public void showList() {
		Set<String> set = phoneBookList.keySet();
		Iterator<String> it =set.iterator();
		System.out.println("\n총 "+phoneBookList.size()
		 				  +" 명의 회원이 저장되어 있습니다.");
		while(it.hasNext()) {
			String phoneNumber = it.next();
			Person person = phoneBookList.get(phoneNumber);
			System.out.print("회원정보 - "+person.toString());
			System.out.println();
		}
		
	}
	
	
	// 5. 회원 정보 수정하기 기능
	public void editPerson(Scanner scanner) {
		if(!phoneBookList.isEmpty()) {
			while(true) {
				System.out.println("\n수정할 회원의 이름을 입력하세요.");
				searchFunction(scanner); 
//				그 이름에 해당하는 회원이 존재하지 않으면 메뉴로 돌아감.
				if(search_list.size()==0) {
					break;
				}
				
				
				while(true) {
					System.out.println("아래 목록 중 수정할 회원의 번호를 입력하세요. \n(0번을 입력하시면 메인메뉴로 돌아갑니다.)");
					for(int i=0; i<search_list.size(); i++) {
						Person person = search_list.get(i);
						System.out.println((i+1)+"."+person.toString());
					}
					
					
					int choice;
					
//				목록에 있는 회원 외의 것을 선택할 때 검증해주는 프로그램.
//				InputMismatch exception 해결 완료.
					try {
						while(((choice = scanner.nextInt()-1)>=search_list.size())||(choice < -1)) {
							System.out.println("선택한 수가 유효하지 않습니다. 수정할 회원의 번호를 다시 입력해주세요.\n0번을 누르시면 메인메뉴로 돌아갑니다.");
						}
						scanner.nextLine();
						// 여기서 입력받는 숫자가 인덱스 숫자보다 작도록 검증완료 
						// 만약에 인덱스 숫자보다 크면 다음 과정 진행되면 안됨.
						if(choice==-1) {
							System.out.println("메인 메뉴로 이동합니다.\n");
							search_list.clear();
							break;
						}
						
						System.out.println("수정할 정보를 입력하세요.");
						System.out.print("이름: ");
						String edited_name = scanner.nextLine();
						String edited_phoneNumber;
						
//					핸드폰번호 또는 집전화형식 아니면 다시 연락처를 받도록 검증함.
						while(true) { 
							System.out.print("연락처(ex: 01023233232 또는 0312442858): ");
							if(numberChecker(edited_phoneNumber=scanner.nextLine())) 
								// 핸드폰 번호 또는 집전화번호 형식만 받아들인다.
							{
								break;
							}
						}
						
//					주소 기입 - 검증하는거 따로 없음.
						System.out.print("주소: ");
						String edited_address = scanner.nextLine();
						String edited_group;
						
//					종류를 입력할 때, 가족,친구,기타 이 세가지 이외의 것을 넣었을 땐 다시 입력하도록 검증.
						while(true) {
							System.out.print("종류(ex.가족, 친구, 기타): ");
							if(groupChecker(edited_group = scanner.nextLine())) { 
								// 종류가 가족 친구 기타 이 세가지인지 아닌지 검증한다.
								break;
							}
						}
						
//						중복시 덮어씌울 것인지 확인하는 기능.
						if(phoneBookList.keySet().contains(edited_phoneNumber)){
							System.out.println(phoneBookList.get(edited_phoneNumber).toString());
							System.out.println("기입한 연락처로 저장되어 있는 회원이 이미 존재합니다.\n기입한 정보로 덮어 씌우시겠습니까? Y/N");
							String choice2=scanner.nextLine();
							if(choice2.matches("Y")||choice2.matches("y")) {
								phoneBookList.remove(search_list.get(choice).getPhoneNumber());
								search_list.get(choice).setName(edited_name); 
								search_list.get(choice).setPhoneNumber(edited_phoneNumber);
								search_list.get(choice).setAddress(edited_address);
								search_list.get(choice).setGroup(edited_group);
								phoneBookList.put(search_list.get(choice).getPhoneNumber(), search_list.get(choice));
								System.out.println("\n수정이 완료되었습니다.\n");
								search_list.clear();
								break;	
							}else if(choice2.matches("N")||choice2.matches("n")) {
								System.out.println("\n기입한 회원의 정보로 갱신하지 않고 메인 메뉴로 돌아갑니다.\n");
								search_list.clear();
								break;
							}else {
								System.out.println("키를 잘못 입력하셨습니다.\n Y 또는 N 으로 다시 기입해주세요.");
								search_list.clear();
							}
						}else {
//							검증받은 수정 후의 이름, 전화번호, 주소, 종류를 각각 담는다.
							phoneBookList.remove(search_list.get(choice).getPhoneNumber());
							search_list.get(choice).setName(edited_name); 
							search_list.get(choice).setPhoneNumber(edited_phoneNumber);
							search_list.get(choice).setAddress(edited_address);
							search_list.get(choice).setGroup(edited_group);
							phoneBookList.put(search_list.get(choice).getPhoneNumber(), search_list.get(choice));
							search_list.clear();
							System.out.println("\n수정이 완료되었습니다.\n");
							break;	
						}		
					}catch(InputMismatchException e) {
						scanner.nextLine();
						System.out.println("숫자를 입력해주세요.");
						continue;
					}
				}
				break;
			}			
			}else {
//			목록에 연락처가 하나도 없을 때는 다시 초기메뉴로 돌아감.
			System.out.println("\n수정할 수 있는 회원이 없습니다.\n");
		}		
	}
	
	// 6. 검색하는 기능
	public void searchFunction(Scanner scanner) {
		System.out.print("이름 : ");
		String name = scanner.nextLine();
//		이름 받아 들였고, 이제 찾아내야 됨.
//		이제 HashMap 반복문 돌려서, 이름이 그 이름이면 search_list 에 추가해야 함.
		Set<String> phoneNumbers = phoneBookList.keySet();
		Iterator<String> it = phoneNumbers.iterator();
		while (it.hasNext()) {
			Person person = phoneBookList.get(it.next());
			if (person.getName().matches(name)) {
				search_list.add(person); // 검색한 이름에 해당하는 사람이 있으면 ArrayList 에 삽입.
			}
		}
		if(search_list.size()==0) {
			System.out.println("\n해당하는 회원 정보가 없습니다.\n");
			return;
		}else {
			System.out.println("총 "+ search_list.size() + "개의 목록이 검색되었습니다.");			
		}
	}
	
	
	// 7. 회원 삭제 기능
	public void removePerson(Scanner scanner) {
//		전화번호부에 적어도 한명이라도 있을 때 다음 단계로 넘어간다.
		if(!phoneBookList.isEmpty()) {
			System.out.println("\n삭제할 회원의 이름을 입력하세요.");			
			searchFunction(scanner);
			
			if(search_list.size()==0) {
				return;
			}
			
			while(true) {
				System.out.println("아래 목록 중 삭제할 회원의 번호를 입력하세요. \n(삭제를 원하지 않을 경우 0번을 입력해주세요.)");			
				if(!search_list.isEmpty()) { 
					for(int i=0; i<search_list.size(); i++) {
						Person person = search_list.get(i);
						System.out.println((i+1)+"."+person.toString());						 
					} 
//					InputMismatchException 처리 완료.
					try {
						int choice;
						while(((choice = scanner.nextInt()-1)>=search_list.size())||(choice < -1)) {
							System.out.println("선택한 수가 유효하지 않습니다. 수정할 회원의 번호를 다시 입력해주세요.\n0번을 누르시면 메인메뉴로 돌아갑니다.");
						}
						scanner.nextLine();
						if(choice == -1) {
							System.out.println("\n메인 메뉴로 돌아갑니다.\n");
							search_list.clear();
							break;
						}
//						인덱스 범위 넘어가는거 예외처리 완료.
						try {
							phoneBookList.remove(search_list.get(choice).getPhoneNumber());
							System.out.println("\n해당 회원의 연락처가 삭제되었습니다.\n");
							search_list.clear(); // 목록이 이제 필요가 없으니 초기화를 시켜준다.
							break;
						}catch(IndexOutOfBoundsException e) {						
							System.out.println("선택한 수가 유효하지 않습니다. \n삭제할 회원의 번호를 다시 입력해주세요.");
						}					
//					숫자가 아닌 인풋 예외 처리. (int choice (선택할 때))
					}catch(InputMismatchException e) {
						scanner.nextLine();
						System.out.println("숫자를 입력해주세요.");
						continue;
					}
				}else {
//					검색 리스트에 내가 검색하는 이름이 없으면 메인메뉴로 돌아간다.
					System.out.println("\n검색하신 이름을 찾을 수 없습니다.\n");
					break;
				}
			}
		}else { // 목록에 연락처가 하나도 없을 땐 메인메뉴로 돌아간다.
			System.out.println("\n삭제할 수 있는 회원이 없습니다.\n");			
		}
	}	
}

